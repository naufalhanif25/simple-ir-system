# Simple IR System CLI

An Information Retrieval (IR) system built using the **Python** programming language with a Command-Line Interface (CLI). The application implements **Bag of Words (BoW) representation** with **Cosine Similarity** for document ranking and integrates **Whoosh** for efficient text indexing and search capabilities. The system supports multiple datasets and features advanced Indonesian text preprocessing. Configuration is managed through JSON files for flexible customization.

## Requirements

Make sure the following are installed on your system:
- Python 3.10 or newer  
- Poetry (optional, for dependency management)

## Installation & Run

1. **Install dependencies**
    Install the dependencies using Poetry
    ```shell
    poetry install
    ```
    or install the dependencies using pip
    ```
    pip install pandas scikit-learn whoosh sastrawi joblib colorama
    ```

2. **Run the program**
    Run the program using `./run.sh`
    ```shell
    chmod +x run.sh
    ./run.sh start
    ```
    or run the program using **Poetry**
    ```shell
    poetry run python main.py
    ```
    or run the program using **Python** if you are not using **Poetry**
    ```shell
    python main.py