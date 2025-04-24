import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
)
from typing import List
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CopartScraper:
    def __init__(self):
        """
        Initialize the scraper with the sheet URL and setup Selenium WebDriver.
        """
        # self.sheet_url = sheet_url
        # self.urls_to_scrape: List[str] = []
        self.driver = self.open_browser()
    
    def open_browser(self):
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        
        # Do NOT use any user profile or user data directory
        # Optional: You can add incognito mode for a cleaner session
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-popup-blocking")

        # Get the correct driver path
        driver_path = ChromeDriverManager().install().replace(
            "THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe"
        )

        # Initialize the browser without a profile
        driver = uc.Chrome(
            driver_executable_path=driver_path, options=options
        )
        return driver

    
    
    # def load_urls_from_sheet(self):
    #     """
    #     Placeholder: Load URLs from the provided sheet URL.
    #     You can implement reading from Google Sheets, CSV, or Excel.
    #     """
    #     print(f"Loading URLs from: {self.sheet_url}")
    #     # Replace this with your logic to pull URLs from a Google Sheet or file
    #     self.urls_to_scrape = [
    #         "https://www.copart.com/lot/12345678",  # Example URL
    #         # Add more URLs
    #     ]
        
    def extract_all_images(self):
        image_urls = []

        # Step 1: Get the first image URL (before any click)
        print(1)
        first_img = self.driver.find_element(By.XPATH, "//img[@id='media-lot-image']")
        print(2)
        image_urls.append(first_img.get_attribute("src"))

        # Step 2: Get 'See all X Photos' element and extract the number X
        print(3)
        see_all_text = self.driver.find_element(By.XPATH, "//span[contains(@class, 'see-all-photos-block') and contains(., 'See all')]").text
        print(4)
        total_photos = int([s for s in see_all_text.split() if s.isdigit()][0])

        # Step 3: Click the "next" button (n - 1) times
        print(5)
        next_button = self.driver.find_element(By.CLASS_NAME, "p-galleria-item-next")        
        for _ in range(total_photos - 1):
            next_button.click()
            time.sleep(1.2)  # wait for the image to load
            
            # Get the new image URL after each click
            current_img = self.driver.find_element(By.XPATH, "//img[@id='media-lot-image']")
            image_urls.append(current_img.get_attribute("src"))
        
        return image_urls



    def scrape_single_url(self, url: str) -> dict:

        print(f"Scraping: {url}")
        self.driver.get(url)
        time.sleep(25)  

        data = {}

        try:
            name = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'title')]").text.strip()
    
            # Collecting lot details
            lot_detail_section = self.driver.find_element(By.XPATH, "//div[contains(@class, 'lot-information')]")
            
            # Collecting various lot details
            lot_number = lot_detail_section.find_element(By.XPATH, ".//span[@id='LotNumber']").text.strip()
            title = lot_detail_section.find_element(By.XPATH, ".//label[@for='SaleTitleDescription']/following-sibling::span//span[1]").text.strip()
            try:
                odometer = lot_detail_section.find_element(By.XPATH, ".//label[@for='Odometer:']/following-sibling::span//span[1]/span[1]").text.strip()
            except NoSuchElementException as e:
                odometer = "N/A"
                
            primary_damage = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailPrimarydamage']/following-sibling::span").text.strip()
            try:
                secondary_damage = lot_detail_section.find_element(By.XPATH,".//label[@data-uname='lotdetailSecondarydamage']/following-sibling::span").text.strip()
            except NoSuchElementException as e:
                secondary_damage = "No secondary damage"
            color = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailColor']/following-sibling::span").text.strip()
            drive = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailDrive']/following-sibling::span").text.strip()
            try:
                has_engine = ""
                engine = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailEngine']/following-sibling::div/span").text.strip()
                if engine == 0 or engine == '0' or engine == 'U':
                    engine = "Electric"
            except NoSuchElementException as e:
                try:
                    has_engine = lot_detail_section.find_element(
                        By.XPATH,
                        ".//label[@data-uname='lotdetailHasEngine']/following-sibling::div//span[@data-uname='lotdetailEnginetype']"
                    ).text.strip()
                    engine = "No"
                except NoSuchElementException:
                    # Fallback if even the alternative engine info is not found
                    engine = "No"
                    has_engine = ""        
            fuel = lot_detail_section.find_element(By.XPATH,".//label[@data-uname='lotdetailFuel']/following-sibling::span").text.strip()
            keys = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailKey']/following-sibling::span").text.strip()
            highlights = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailHighlights']/following-sibling::div//span[1]").text.strip()
            try:
                seller = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailSeller']/following-sibling::div//span").text.strip()
            except NoSuchElementException as e:
                seller = "No seller information"
            notes = lot_detail_section.find_element(By.XPATH, ".//label[@data-uname='lotdetailNotes']/following-sibling::div//div[@data-uname='lotdetailNotesvalue']").text.strip()
            
            # Collecting location information
            location = self.driver.find_element(
                By.XPATH,
                "//div[@id='sale-information-block']//label[@data-uname='lotdetailSaleinformationlocationlabel']/following-sibling::span//a"
            ).text.strip()

            # Check for the 'Listen to engine' component and its content
            listen_to_engine_component = self.driver.find_element(By.XPATH, "//listen-to-engine-component")
            
            # Check if the component contains any child content (e.g., a span with text inside)
            if listen_to_engine_component.find_elements(By.XPATH, ".//span[contains(@class, 'p-fs-12')]"):
                engine_video = True  
            else:
                engine_video = False
                
            time.sleep(3)
            image_urls = self.extract_all_images()
            
            
            
            # Storing all the collected data in the dictionary
            data = {
                "name": name,
                "lot_number": lot_number,
                "title": title,
                "odometer": odometer,
                "primary_damage": primary_damage,
                "secondary_damage": secondary_damage,
                "color": color,
                "fuel": fuel,
                "drive": drive,
                "engine": engine,
                "has_engine": has_engine,
                "keys": keys,
                "highlights": highlights,
                "seller": seller,
                "notes": notes,
                "location": location,
                "engine_video_exists": engine_video, 
                "images" : image_urls
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")

        return data

    def close(self):
        """
        Cleanly close the Selenium driver.
        """
        self.driver.quit()

# if __name__:
#     copart_scraper = CopartScraper("https://docs.google.com/spreadsheets/d/195mIW2xZcJh4RymPUavzhPfURhaKFs4WCoQ404ED_RM")
#     data = copart_scraper.scrape_single_url("https://www.copart.com/lot/89115265/salvage-2022-kia-ev6-light-il-chicago-north")
#     print(data)