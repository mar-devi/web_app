from myapp.search.algorithms import search_in_corpus


class SearchEngine:
    """educational search engine"""
    
    def search(self, search_query, search_id, corpus):

        print("Search query:", search_query)

        results = search_in_corpus(corpus, search_id,search_query)
                
        return results
