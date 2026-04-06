from agents import Agent,Runner, ImageGenerationTool,input_guardrail,GuardrailFunctionOutput, InputGuardrailTripwireTriggered,RunContextWrapper,output_guardrail
from lib.files import retrieve_image_from_resources, open_file
import base64
from pydantic import BaseModel
from lib.tools import save_design_data_to_database


class GuardrailAgentOutput(BaseModel):
    is_not_allowed: bool
    reason: str | None = None 


guardrail_agent = Agent(
    name="Floorplan Checker Agent",
    instructions= '''
        Check if the image that the user has submitted is valid floorplan and that the user's design preference input is actually relevant to the intetior design.The user must not ask for any thing offensive or not safe for work.
    ''',
    tools = [],
    output_type=GuardrailAgentOutput
)

@input_guardrail
async def guardrail_function(ctx: RunContextWrapper,agent: Agent, input_data: str) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent,input_data)
    return GuardrailFunctionOutput(
        output_info=result.final_output.reason,
        tripwire_triggered=result.final_output.is_not_allowed
    )
async def validate_output(ctx, agent, output):
    try:
        DesignOutput(**output)
        return GuardrailFunctionOutput(
            output_info="Valid output",
            tripwire_triggered=False
        )
    except Exception as e:
        return GuardrailFunctionOutput(
            output_info=str(e),
            tripwire_triggered=True
        )



class DesignOutput(BaseModel):
    rooms:list[str]
    design_style: str
    color_pallete: list[str]
    furniture: list[str]


my_agent = Agent(
    name= "Interior design agent",
    instructions = """You are an interior design agent specialized in creating ethnic-style home interiors. You generate design images for each room in a home based on the floorplan provided by the user.

You should approach the problem using this process:

1. Identify all the rooms in the submitted floorplan image.
2. Estimate realistic dimensions and proportions of each room based on the layout.
3. Design each room using ethnic interior styles (e.g., traditional Indian, rustic, cultural, handcrafted aesthetics), while also incorporating the user's specific preferences.
4. Carefully plan furniture placement, decor elements, textures, and color schemes, ensuring alignment with visible structural elements such as doors and windows.
5. Generate exactly one image per valid room (excluding hallways).
6. After generating all images, save the complete interior design details for the entire floorplan in a single database entry using the tool `save_design_data_to_database`. Do not create multiple entries.

Ethnic Design Guidelines:
- Use culturally inspired elements such as wooden furniture, carved details, traditional patterns, textiles, earthy tones, and warm lighting.
- Maintain authenticity and avoid mixing unrelated modern or futuristic styles unless explicitly requested.
- Ensure each room has a distinct yet cohesive ethnic theme.

Image Generation Guidelines:
- Ensure each generated image accurately reflects the corresponding room layout from the floorplan.
- Use a wide-angle camera perspective that captures the full room clearly.
- Do not add or remove architectural elements like doors or windows that are not present in the floorplan.
- Do not generate images for hallways or undefined spaces.
- Generate a maximum of 5 images in total.

Output:
Return the final output including all generated images. Do not include text links to the images. Ensure the output is clean and directly usable.
    """,
    tools=[
        ImageGenerationTool({
            "type": "image_generation",
            "output_format":"png",
            "quality": "high", #may take time to generate good quality images you can switch to low 
            "size": "1024x1024"
        }),
        save_design_data_to_database
    ],
    model= "gpt-4o",
    input_guardrails=[
        guardrail_function
    ],
    output_guardrails=[validate_output]
)
async def run_agent(design_style:str,floorplan_image:str):
    image = retrieve_image_from_resources(floorplan_image)
    formatted_input = [
        {
            "role":"user",
            "content": [
                {
                    "type":"input_image",
                    "image_url": f"data:image/jpeg;base64,{image}"
                },
                {
                    "type":"input_text",
                    "text":design_style
                }
            ]
        }
    ]

    try:
        result = await Runner.run(my_agent,formatted_input)

        image_paths = []
        image_count=0
        for item in result.new_items:
            if(
                item.type == "tool_call_item" 
                and item.raw_item.type == "image_generation_call"
                and (img_result := item.raw_item.result)
            ):
                with open(f"output/generated_image_{image_count}.png","wb") as f:
                    f.write(base64.b64decode(img_result))
                    image_paths.append(f"output/generated_image_{image_count}.png")
                    image_count += 1
                    open_file(f"output/generated_image_{image_count}.png")
    except InputGuardrailTripwireTriggered as e:
        print("Input Guardrail Triggered: ",e)