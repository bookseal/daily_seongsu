import random
from datetime import datetime, timedelta

class SeongsuScraper:
    def __init__(self):
        self.hashtags = ["#성수팝업", "#성수동", "#팝업스토어"]

    def fetch_data(self):
        """
        Simulates fetching data from external sources.
        Returns a list of popup store dictionaries.
        """
        print("Fetching data from simplified sources...")
        
        # Mock data generation
        popups = []
        titles = [
            "Tamburins Perfume Exhibition", 
            "Dior Seongsu Pop-up", 
            "Musinsa Standard Pop-up",
            "Gentle Monster Haus",
            "Ader Error Space"
        ]
        images = [
            "https://placehold.co/600x400/png?text=Tamburins",
            "https://placehold.co/600x400/png?text=Dior",
            "https://placehold.co/600x400/png?text=Musinsa",
            "https://placehold.co/600x400/png?text=Gentle+Monster",
            "https://placehold.co/600x400/png?text=Ader+Error"
        ]
        
        for i in range(5):
            popup = {
                "id": f"popup_{i}",
                "title": titles[i],
                "description": f"Experience the new {titles[i]} in the heart of Seongsu.",
                "image_url": images[i],
                "start_date": (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d"),
                "end_date": (datetime.now() + timedelta(days=random.randint(5, 20))).strftime("%Y-%m-%d"),
                "location": "Seongsu-dong 2-ga, Seongdong-gu, Seoul",
                "source": "Instagram"
            }
            popups.append(popup)
            
        return popups
