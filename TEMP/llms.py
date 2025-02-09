import os
import ai

from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel(
    model_name=os.getenv("GEMINI_MODEL"),
    project_id=os.getenv("VERTEX_AI_PROJECT_ID"),
)


