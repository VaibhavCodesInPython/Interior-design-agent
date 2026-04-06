from pydantic import BaseModel
from agents import function_tool
class DesignDatabaseEntry(BaseModel):
    rooms:list[str]
    design_style: str
    color_pallete: list[str]
    furniture: list[str]
    model_config = {
        "extra" : "forbid"
    }

@function_tool
async def save_design_data_to_database(data:DesignDatabaseEntry) -> str:
    print("Design data saved to the database:",data)

    with open("output/design_output.txt",'w') as f:
        f.write(str(data))
