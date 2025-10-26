import os
import pandas as pd
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer
from whoosh.index import FileIndex
from whoosh.index import open_dir
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.metrics.pairwise import cosine_similarity
from whoosh.qparser import QueryParser
from colorama import Fore, Style
from numpy import ndarray
import warnings
import joblib
import re
import pickle
import json
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

warnings.filterwarnings("ignore", category = InconsistentVersionWarning)

global_datasets_path: str = "datasets/"
global_bow_path: str = "content/bow_data.joblib"
global_whoosh_index: str = "content/whoosh_index"
global_json_path: str = "irs_config.json"

with open(global_json_path, "r", encoding = "utf-8") as json_file:
    global_irs_config: dict = json.load(json_file)
    
class TextPreprocessor:
    def __init__(self):
        self.stopword_factory = StopWordRemoverFactory()
        self.stopword_remover = self.stopword_factory.create_stop_word_remover()
        self.stemmer_factory = StemmerFactory()
        self.stemmer = self.stemmer_factory.create_stemmer()
    
    def case_folding(self, text: str) -> str:
        return text.lower()
    
    def clean_text(self, text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    def remove_stopwords(self, text: str) -> str:
        return self.stopword_remover.remove(text)
    
    def stem_text(self, text: str) -> str:
        return self.stemmer.stem(text)
    
    def preprocess_text(self, text: str) -> str:
        text = str(text)
        text = self.case_folding(text)
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        text = self.stem_text(text)
        
        return text.strip()
    
class DocumentProcessor:
    def __init__(self):
        self.vectorizer = CountVectorizer()

    def load_data(self, filename: str) -> list[any]:
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                dataframe_list = pickle.load(file)

            print(f"{Fore.RED}>{Style.RESET_ALL} Indexed data successfully loaded [{Fore.YELLOW}path: {filename}{Style.RESET_ALL}]")

            return dataframe_list
        else:
            print(f"{Fore.RED}>{Style.RESET_ALL} No such file or directory [{Fore.YELLOW}path: {filename}{Style.RESET_ALL}]")

            return []

    def load_data_joblib(self, filename: str) -> any:
        bow_data = joblib.load(filename)
        self.vectorizer = bow_data['vectorizer']

        print(f"{Fore.RED}>{Style.RESET_ALL} BoW data successfully loaded [{Fore.YELLOW}path: {filename}{Style.RESET_ALL}]")

        return bow_data['bow_matrix'], bow_data['feature_names'], bow_data['doc_ids']

    def load_whoosh_index(self, index_dir: str = "whoosh_index") -> FileIndex:
        if os.path.exists(index_dir):
            try:
                ix = open_dir(index_dir)

                print(f"{Fore.RED}>{Style.RESET_ALL} Whoosh index successfully loaded [{Fore.YELLOW}path: {index_dir}{Style.RESET_ALL}]")

                return ix
            except Exception as e:
                print(f"{Fore.RED}>{Style.RESET_ALL} Error loading Whoosh index [{Fore.RED}error: {e}{Style.RESET_ALL}]")
                
                return None
        else:
            print(f"{Fore.RED}>{Style.RESET_ALL} Whoosh index directory not found [{Fore.YELLOW}path: {index_dir}{Style.RESET_ALL}]")

            return None
    
class SearchEngine:
    def __init__(self, document_processor: any, bow_matrix: any, feature_names: any, doc_ids: any, ix: any, dataframes: list[DataFrame]):
        self.document_processor = document_processor
        self.bow_matrix = bow_matrix
        self.feature_names = feature_names
        self.doc_ids = self._ensure_list(doc_ids)
        self.ix = ix
        self.dataframes = dataframes
        self.vectorizer = document_processor.vectorizer

    def _ensure_list(self, data):
        if isinstance(data, pd.DataFrame):
            return data.iloc[:, 0].tolist()
        elif isinstance(data, pd.Series):
            return data.tolist()
        elif isinstance(data, list):
            return data
        else:
            try:
                return list(data)
            except Exception:
                raise
    
    def search_with_cosine_ranking(self, query_text: str, top_k: int = 30, max_limit: int | None = 100) -> list:
        preprocessed_query = self._preprocess_query(query_text)

        if preprocessed_query is None or preprocessed_query == "":
            return []
        
        print(f"Hasil pencarian dari query '{Fore.YELLOW}{query_text}{Style.RESET_ALL}'")

        whoosh_results = self._whoosh_search(preprocessed_query, limit = max_limit)        
        
        if not whoosh_results:
            return []

        print(f"Total {Fore.CYAN}{len(whoosh_results)}{Style.RESET_ALL} dokumen terkait ditemukan\n")

        query_vector = self.vectorizer.transform([preprocessed_query])
        ranked_results = self._calculate_cosine_similarity(whoosh_results, query_vector)
        final_results = ranked_results[:top_k]
        
        print(f"Berikut adalah {Fore.CYAN}{len(final_results)}{Style.RESET_ALL} dokumen teratas:")
        
        return final_results
    
    def _preprocess_query(self, query_text: str) -> str:
        text_preprocessor = TextPreprocessor()

        return text_preprocessor.preprocess_text(query_text)
    
    def _whoosh_search(self, query_text: str, limit: int | None = 100) -> list:
        with self.ix.searcher() as searcher:
            query_parser = QueryParser("konten", self.ix.schema)
            query = query_parser.parse(query_text)
            results = searcher.search(query, limit = limit)
            results_data = []
            
            for result in results:
                result_data = {
                    "doc_id": result["doc_id"],
                    "source": result["source"],
                    "judul": result["judul"],
                    "konten": result["konten"],
                    "score": result.score
                }
                results_data.append(result_data)
            
            return results_data
    
    def _calculate_cosine_similarity(self, whoosh_results: list, query_vector: any) -> list:
        similarities = []
        
        for whoosh_result in whoosh_results:
            doc_id = whoosh_result["doc_id"]

            if doc_id in self.doc_ids:
                doc_index = self.doc_ids.index(doc_id)
                doc_vector = self.bow_matrix[doc_index]
                similarity = cosine_similarity(query_vector, doc_vector)[0][0]
                
                similarities.append((doc_id, similarity, whoosh_result))

        similarities.sort(key = lambda x: x[1], reverse = True)

        return similarities
    
    def display_results(self, results: list, truncate: int = 100) -> None:
        if not results:
            print(f"{Fore.BLUE}>{Style.RESET_ALL} {Fore.RED}Tidak ada dokumen terkait yang ditemukan{Style.RESET_ALL}")

            return
        
        document_list = os.listdir(global_datasets_path)
 
        for i, (doc_id, similarity, whoosh_result) in enumerate(results):
            doc_positions = str(doc_id).split("_")[1:]
            doc_index, line_index = [int(doc_pos) for doc_pos in doc_positions]

            judul_result = self.dataframes[doc_index - 1].loc[line_index - 1, 'judul']
            judul_result = str(judul_result[:truncate]).title() + "..." if len(judul_result) > truncate else judul_result

            konten_result = self.dataframes[doc_index - 1].loc[line_index - 1, 'konten']
            konten_result = str(konten_result[:truncate * 2]).capitalize() + "..." if len(konten_result) > truncate * 2 else konten_result

            print(f"{Fore.RED}{i + 1}.{Style.RESET_ALL} {Fore.GREEN}{judul_result}{Style.RESET_ALL} [{Fore.YELLOW}sim: {similarity * 100:.3f}%{Style.RESET_ALL}] [{Fore.YELLOW}from: {Fore.BLUE}{os.path.join(global_datasets_path, document_list[int(whoosh_result['source'][-1]) - 1])}{Style.RESET_ALL}]")
            print(f"    {Fore.YELLOW}->{Style.RESET_ALL} {Fore.WHITE}{Style.DIM}{konten_result}{Style.RESET_ALL}")

if __name__ == "__main__":
    bow_matrix: ndarray | None = None
    feature_names: ndarray | None = None
    doc_ids: list | None = None
    ix: FileIndex | None = None
    
    document_processor = DocumentProcessor()

    dataset_path_list: list[str] = [os.path.join(global_datasets_path, dataset_path) for dataset_path in os.listdir(global_datasets_path)]
    dataframe_list: list[DataFrame] = []

    for dataset_path in dataset_path_list:
        dataframe_list.append(pd.read_csv(dataset_path, header = 0, sep = ","))

    while True:
        print(f"--- {Fore.GREEN}{Style.BRIGHT}Information Retrieval System{Style.RESET_ALL} ---")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Load Indexed Data")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Search Query")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Exit")
        print("------------------------------------")
        
        input_val = 0

        try:
            input_val = int(input(f"{Fore.BLUE}>{Style.RESET_ALL} "))

            if input_val > 3 or input_val < 1:
                input_val = 0
        except Exception:
            pass

        if input_val in (0, 1, 2):
            print("\n", end = "")

        if input_val == 1:
            print(f"{Fore.RED}Logs:{Style.RESET_ALL}")
            bow_matrix, feature_names, doc_ids = document_processor.load_data_joblib(global_bow_path)
            ix = document_processor.load_whoosh_index(global_whoosh_index)
        elif input_val == 2:
            if bow_matrix is None or feature_names is None or doc_ids is None or ix is None:
                print(f"{Fore.YELLOW}>{Style.RESET_ALL} {Fore.RED}Indexed data has not been loaded{Style.RESET_ALL}")
                print("\n", end = "")
                
                continue

            search_engine = SearchEngine(document_processor, bow_matrix, feature_names, doc_ids, ix, dataframe_list)

            query = input(f"{Fore.BLUE}Query:{Style.RESET_ALL} ")

            results_limit = global_irs_config.get("configs").get("lim")
            results_limit = global_irs_config.get("configs").get("max_k") if results_limit else None

            results = search_engine.search_with_cosine_ranking(query, top_k = global_irs_config.get("configs").get("top_k"), max_limit = results_limit)
            search_engine.display_results(results, truncate = global_irs_config.get("configs").get("tr_len"))
        elif input_val == 3:
            break
        else:
            print(f"{Fore.YELLOW}>{Style.RESET_ALL} {Fore.RED}Option is not available{Style.RESET_ALL}")
            print("\n", end = "")

            continue

        if input_val in (0, 1, 2):
            print("\n", end = "")