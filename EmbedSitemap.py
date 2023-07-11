import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.document_loaders import TextLoader
from langchain.document_loaders.sitemap import SitemapLoader

class EmbedSitemap:
  def __init__(self, url="", deeplake_username="", deeplake_db=""):
    self.url = url
    self.deeplake_username = deeplake_username
    self.deeplake_db = deeplake_db
    self.embeddings = OpenAIEmbeddings(disallowed_special=())
    self.db = DeepLake(
      dataset_path=f"hub://{self.deeplake_username}/{self.deeplake_db}",
      embedding_function=self.embeddings,
    )
  
  # Split the files into chunks
  def split(self):
    sitemap_loader = SitemapLoader(web_path=self.url)
    docs = sitemap_loader.load()
    return docs
  
  # Save the embeddings
  def save(self, texts):
    self.db.add_documents(texts)

# embed = EmbedSitemap(...)
# texts = embed.split()
# embed.save(texts)
