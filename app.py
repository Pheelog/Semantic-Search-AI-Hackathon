import streamlit as st
import cohere
import numpy as np
import faiss

st.markdown("""
    <img src=".\images\covid_pic.jpg" alt="My brand logo"/>
""", unsafe_allow_html=True)


# Paste your API key here. Remember to not share publicly
api_key = "lhNxyU2hx99v6EvkwTqi9hykwpTgaL7cHKWSYd2M"

class SemanticSearch():

    def __init__(self, path, key):
        self.co = cohere.Client(key)
        self.embeddings = np.load(path,allow_pickle=True)
        self.index = faiss.IndexFlatIP(self.embeddings['embeddings'].shape[-1])  # inner product index
        f32_embeddings = self.embeddings['embeddings'].astype(np.float32)  # faiss only supports f32

        # normalise embeddings, so that the inner product is the cosine similarity
        normal_f32_embeddings = f32_embeddings / np.linalg.norm(f32_embeddings, ord=2, axis=-1, keepdims=True)
        self.index.add(normal_f32_embeddings)
        
    def query(self, query, num_query=10):
        q_embedding = self.co.embed([query], model='multilingual-22-12').embeddings
        q = np.array(q_embedding, dtype=np.float32)

        # normalise the query too
        normal_q = q / np.linalg.norm(q, ord=2, axis=-1, keepdims=True)
        distances, ind = map(np.squeeze, self.index.search(normal_q, num_query))

        results = []
        for i, dist in zip(ind, distances):
            result = {
                "question": self.embeddings['questions'][i],
                "url": self.embeddings['url'][i],
                "answer": self.embeddings['answer'][i],
            }
            results.append(result)
        return results



st.title("Welcome to Multi Lingual COVID-19 related Search")

search = SemanticSearch("model/semantic_search.npz", api_key)


query = st.text_input("Enter your query", "COVID")

x = st.slider("Select an number of queries", 2, 25, 3)

results = search.query(query, int(x))

for r in results:


    st.markdown("#### Question:")
    st.write("Question: ", "\t",r["question"])
    st.markdown("#### Answer:")
    st.write("\t", r["url"], r["answer"]) #here u can add designs to the output
    st.write("-"*80)
# st.write(f"{results}")
