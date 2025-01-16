import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
from functools import reduce
import matplotlib.pyplot as plt
import threading


def fetch_and_clean_text(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()


def clean_text(text):
    return re.findall(r"\b\w+\b", text.lower())


def map_reduce_word_count(words):
    mapped_words = [(word, 1) for word in words]
    return reduce(
        lambda counter, pair: counter.update([pair[0]]) or counter,
        mapped_words,
        Counter(),
    )


def visualize_top_words(word_counts, top_n=10):
    most_common = word_counts.most_common(top_n)
    words, counts = zip(*most_common)

    plt.barh(words, counts, color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title("Top 10 Most Frequent Words")
    plt.gca().invert_yaxis()
    plt.show()


def threaded_word_count(words, num_threads=4):
    chunk_size = len(words) // num_threads
    threads = []
    results = []

    def worker(start, end):
        sub_result = map_reduce_word_count(words[start:end])
        results.append(sub_result)

    for i in range(num_threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_threads - 1 else len(words)
        thread = threading.Thread(target=worker, args=(start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    final_result = Counter()
    for result in results:
        final_result.update(result)

    return final_result


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Fairy_Tail"
    try:
        raw_text = fetch_and_clean_text(url)
        words = clean_text(raw_text)
        word_count_result = threaded_word_count(words)
        visualize_top_words(word_count_result)

    except requests.RequestException as e:
        print(f"Error fetching text: {e}")
