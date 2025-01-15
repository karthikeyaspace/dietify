from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.chains.llm import LLMChain

import os
import json
import pandas as pd
from pydantic import BaseModel
from typing import List

from config import env

llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=env["GOOGLE_API_KEY"],
)

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=env['GOOGLE_API_KEY']
)

DATASET = "data/data.csv"
FAISS_STORE = "store"


class User(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    height: int
    weight: int
    diet_type: List[str]  # paleo, vegan, keto, mediterranean, dash
    cuisine: List[str]
    allergies: List[str] | None
    calorie_goal: int


class App():
    def __init__(self):
        self.embeddings_model = embeddings_model
        self.store = None
        self.prompt_template = PromptTemplate(
            input_variables=["age", "gender", "height", "weight",
                             "diet_type", "cuisine", "allergies", "calorie_goal", "recipes"],
            template=(
                "Create a detailed 1-day balanced meal plan for a person "
                "{age}-year-old {gender} who is {height} cm tall and weighs {weight} kg. "
                "The user prefers {diet_type} diet type and enjoys {cuisine} cuisines. "
                "They have a daily calorie goal of {calorie_goal} kcal. "
                "Make sure the plan avoids these allergens: {allergies}. "
                "Each day should have 3 meals (breakfast, lunch, dinner) and a snack. "
                "The meals must be diverse and balanced, including details of calories, protein, "
                "carbs, and fat for each meal. Use the following recipes: {recipes}\n\n"
                "Format the response as a JSON object with the following structure:\n"
                "{{\n"
                "  \"meals\": [\n"
                "    {{\"name\": \"meal name\", \"calories\": 0, \"protein\": 0, \"carbs\": 0, \"fat\": 0, \"position\": 1}},\n"
                "    {{\"name\": \"meal name\", \"calories\": 0, \"protein\": 0, \"carbs\": 0, \"fat\": 0, \"position\": 2}},\n"
                "    {{\"name\": \"meal name\", \"calories\": 0, \"protein\": 0, \"carbs\": 0, \"fat\": 0, \"position\": 3}},\n"
                "    {{\"name\": \"snack name\", \"calories\": 0, \"protein\": 0, \"carbs\": 0, \"fat\": 0, \"position\": 4}}\n"
                "  ]\n"
                "}}\n"
                "meal name should be the name of the recipe, and position should be the meal number.\n"
                "Ensure the response is valid JSON and can be parsed by Python's `json.loads()` function.\n"
                "Do not generate any note or explanation at the end of the JSON response.\n"
                "Make sure the diet made be diverse so the user dont get bored of the same food that day, the trade off here can be the calorie intake"
                "the user can have a little more or less calories than the goal but the diet should be diverse and balanced. "

            )
        )

    # initialization of vector stoer
    def vector_store(self):
        if os.path.exists(FAISS_STORE):
            print("Faiss path exists")
            self.store = FAISS.load_local(
                FAISS_STORE,
                embeddings=self.embeddings_model,
                # so that we can load existing model from disc, this is dangerous because the pkl file can be anything
                allow_dangerous_deserialization=True
            )

        else:
            path = os.path.join(os.getcwd(), FAISS_STORE)
            os.mkdir(path)
            print("Faiss path created")
            self.create_embeddings()

    # generating embeddings and storing em in faiss store

    def create_embeddings(self):

        data = pd.read_csv(DATASET)
        documents = [
            Document(
                page_content=f"Recipe: {row['Recipe_name']}, Cuisine: {
                    row['Cuisine_type']}, "
                f"Protein: {row['Protein(g)']}g, Carbs: {row['Carbs(g)']}g, Fat: {
                    row['Fat(g)']}g",
                metadata={"Diet_type": row["Diet_type"],
                          "Recipe_name": row["Recipe_name"]}
            )
            for _, row in data.iterrows()
        ]

        self.store = FAISS.from_documents(documents, self.embeddings_model)
        self.store.save_local(FAISS_STORE)
        print("Embeddings created from dataset")

    def get_similar_docs(self, query: str, k: int = 20):
        if not self.store:
            self.vector_store()
        docs = self.store.similarity_search(query, k=k)
        return docs

    def generate_response(self, user_profile: User):

        # Retrieve relevant recipes from the vector store
        docs = self.get_similar_docs(
            query=', '.join(user_profile.cuisine) +
            ', '.join(user_profile.diet_type)
        )

        print("Docs-", docs)

        recipe_list = [
            f"Recipe: {doc.metadata['Recipe_name']}, {doc.page_content}"
            for doc in docs
        ]

        diet_type_str = ', '.join(user_profile.diet_type)
        cuisine_str = ', '.join(user_profile.cuisine)
        allergies_str = ', '.join(
            user_profile.allergies) if user_profile.allergies else 'none'
        recipes_str = "\n".join(recipe_list)

        chain = LLMChain(llm=llm, prompt=self.prompt_template)

        response = chain.invoke({
            "age": user_profile.age,
            "gender": user_profile.gender,
            "height": user_profile.height,
            "weight": user_profile.weight,
            "diet_type": diet_type_str,
            "cuisine": cuisine_str,
            "allergies": allergies_str,
            "calorie_goal": user_profile.calorie_goal,
            "recipes": recipes_str
        })

        print("AI Response-", response)

        format_res = response['text'].strip()
        if format_res.startswith("```json") and format_res.endswith("```"):
            format_res = format_res[7:-3].strip()

        print("Formated Response-", format_res)

        try:
            res = json.loads(format_res)
            print(type(res), res)
            return res
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None

    def regenerate_response(self, query: str, user_profile: User, prev_response: dict):
        return f"Regenerate api for query '{query}' and user_profile '{user_profile}' and prev_response '{prev_response}'"



ai = App()