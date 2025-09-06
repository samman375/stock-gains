import fear_and_greed

def fearAndGreedIndex():
    """
    Fetches and displays the current CNN Fear and Greed Index.
    """
    data = fear_and_greed.get()
    
    if data:
        index_value = round(float(data.value), 2)
        index_classification = data.description

        print(f"\nCurrent CNN Fear and Greed Index: {index_value}/100 ({index_classification})\n")
