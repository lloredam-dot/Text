# Advanced Text Analysis and Sentiment Tool

This Python script is a powerful and interactive command-line tool for performing natural language processing (NLP) on text files. It analyzes word frequencies, cleans the text by removing "stopwords," and conducts a detailed sentiment analysis.

The primary goal is to demonstrate the impact of data cleaning and to extract meaningful insights from a body of text, such as identifying key themes and gauging the overall sentiment.

## ✨ Features

- **Dynamic File Loading**: Reads and processes both plain text (`.txt`) and PDF (`.pdf`) files.
- **Automated Dependency Management**: Can automatically detect and install missing Python libraries (`nltk`, `spacy`, `PyPDF2`, `scikit-learn`).
- **Comprehensive Stopword Removal**: Aggregates stopwords from three professional NLP libraries (NLTK, spaCy, and Scikit-learn) for a thorough cleaning. It also automatically downloads required NLTK data.
- **Interactive Stopword Refinement**: After an initial cleaning, the user can review the most frequent words and add custom words to the stopword list for a more refined analysis.
- **Comparative Frequency Analysis**: Generates side-by-side bar charts to visually compare the most frequent words **before** and **after** stopword removal, clearly demonstrating the effect of cleaning.
- **Detailed Sentiment Analysis**:
    - Analyzes each sentence to classify it as **Positive**, **Negative**, or **Neutral** based on a built-in sentiment lexicon.
    - Provides a summary of the sentiment distribution across the entire document.
    - Identifies the most frequently used positive and negative words in the text.
- **Rich Data Visualization**: Uses `matplotlib` to create clear and insightful visualizations for both frequency and sentiment analysis results.

## 🚀 How to Use

1.  **Place your file**: Make sure the `.txt` or `.pdf` file you want to analyze is in the same directory as the script.

2.  **Run the script**: Open your terminal or command prompt and run the script using Python.

    ```sh
    python 02_03_combinacion_TXTPDF_M_sentiments.py
    ```

3.  **Step 1: Configure Analysis**:
    - The script will first ask for the **file name** (e.g., `1984.pdf` or `Miser.txt`).
    - It will then ask for the **number of top words** you want to see in the frequency analysis (e.g., `15`).

4.  **Step 2 & 3: Initial Analysis**:
    - The script will perform an initial analysis and display the top words before and after cleaning.
    - A graph will be shown comparing the results. Close the graph window to continue.

5.  **Step 4: Refine Stopwords (Interactive)**:
    - The script will show you the most common words that remain after the first cleaning.
    - You will be prompted to add any of these words (or others) to the stopword list if you consider them to be noise.
    - You can repeat this process, view the current stopword list, or continue to the next step.

6.  **Step 5: Sentiment Analysis**:
    - The script will analyze the sentiment of each sentence and print the results.
    - It will then display a summary of the overall sentiment of the document.
    - Two graphs (a pie chart and a bar chart) will be shown visualizing the sentiment distribution. Close the window to proceed.

7.  **Step 6: Final Visualization**:
    - Finally, the script will show a final comparison graph: the original word frequencies vs. the frequencies after your refined cleaning.

## ⚙️ Dependencies

The script requires the following Python libraries: `nltk`, `spacy` (and its `en_core_web_sm` model), `scikit-learn`, `PyPDF2`, `matplotlib`.

The script includes a function to install these automatically. If you prefer to install them manually, you can use pip:
```sh
pip install nltk spacy scikit-learn PyPDF2 matplotlib
python -m spacy download en_core_web_sm
```
