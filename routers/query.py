import os
from datetime import datetime
import logging

from fastapi import APIRouter

from index.inverted_index import InvertedIndex
from index.processor import Processor
from main import app
from routers.models import SimilarDocs


logger = logging.getLogger(__name__)

router = APIRouter()

files = {"LEXICON_FILE": "", "INVERTED_FILE": "", "DOCUMENT_LENGTH_FILE": ""}


@app.on_event("startup")
async def startup_event():
    """Find latest pre-computed index files."""
    dataset = os.getenv("DATASET")

    latest_date = datetime.min

    for file in os.listdir("output_reports"):
        if dataset in file and "_" in file:
            date_str = file.split("_")[-1].replace(".csv", "").replace(".bin", "")
            date = datetime.strptime(date_str, "%d%m%Y-%H%M%S")

            if date >= latest_date:
                latest_date = date

                if "document_length" in file:
                    files["DOCUMENT_LENGTH_FILE"] = f"output_reports/{file}"
                elif "index" in file:
                    files["INVERTED_FILE"] = f"output_reports/{file}"
                elif "lexicon" in file:
                    files["LEXICON_FILE"] = f"output_reports/{file}"

    logger.info("Loaded document length file %s", files["DOCUMENT_LENGTH_FILE"])
    logger.info("Loaded index file %s", files["INVERTED_FILE"])
    logger.info("Loaded lexicon file %s", files["LEXICON_FILE"])


@router.post("/query", response_model=SimilarDocs)
async def query(query_str: str, limit: int = 10, offset: int = 0):
    """Find relevant documents, given a query term."""
    processor = Processor()
    tokenized_query = processor.process_line(query_str)

    index = InvertedIndex()

    df = index.cosine_similarity(
        files["LEXICON_FILE"],
        files["INVERTED_FILE"],
        files["DOCUMENT_LENGTH_FILE"],
        tokenized_query,
    )
    sorted_docs = df.sort_values(by=["cosine_score"])["doc_id"].to_list()

    end_index = offset + limit

    return {"documents": sorted_docs[offset:end_index]}
