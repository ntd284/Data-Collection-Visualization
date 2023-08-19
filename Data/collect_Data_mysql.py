from bs4 import BeautifulSoup
import requests
import re
from time import sleep
from sqlalchemy import create_engine, Column, Integer, String, JSON,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import re

def Mysql(rows):
    Base = declarative_base()
    class Specs(Base):
        __tablename__ = 'Specs'
        id = Column(Integer, primary_key=True)
        Max_Resolution = Column(String(255))
        DisplayPort = Column(String(255))
        HDMI = Column(String(255))
        DirectX = Column(String(255))
        Model = Column(String(255))
    class Prod_Info(Base):
        __tablename__ = 'Prod_Info'
        id = Column(Integer, primary_key=True)
        ItemID = Column(String(255))
        Title = Column(String(255))
        Branding = Column(String(255))
        Rating = Column(Float)
        Num_rating = Column(Integer)
        Price = Column(Float)
        Shipping = Column(String(255))
        Image_Url = Column(String(255))
        Specs_data = Column(JSON)
        Total_Price = Column(Float)
    engine = create_engine('mysql+mysqlconnector://root:Nokia5530@localhost:3306/Newegg_db')
    Base.metadata.create_all(engine)
    for row in rows:
        print(row)
        if row['Shipping'] == "Shipping" or row['Shipping'] == "Null":
            ship_price = 0.0
        else:
            ship_price = str(re.findall("\d+\.\d+",str(row['Shipping']))).replace("['","").replace("']","")
            if ship_price in "[]":
                ship_price = 0.0
            else:
                ship_price = float(ship_price)
        Specs_data = {  'Max_Resolution': row['Spectification']['Max_Resolution'],
                        'DisplayPort': row['Spectification']['DisplayPort'],
                        'HDMI': row['Spectification']['HDMI'],
                        'DirectX': row['Spectification']['DirectX'],
                        'Model': row['Spectification']['Model']}       
        Pro_data = Prod_Info(ItemID=row['ItemID'], 
                    Title=row['Title'], 
                    Branding=row['Branding'],
                    Rating=row['Rating'],
                    Num_rating=row['Num_rating'],
                    Price=row['Price'],
                    Shipping=ship_price,
                    Image_Url=row['Image_Url'],
                    Specs_data=Specs_data,
                    Total_Price = float(float(row['Price']) + ship_price)
                    )
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(Pro_data)
        session.commit()

def regex(var1,var2,strV):
    regexVar = re.search(f"{var1}(.+?){var2}",strV).group(1)
    return regexVar

def extract_data(Spec,count):
    count+=1
    id = Spec.find('div')['id']
    print(f"{count}. {id}")
    Data_feas= Spec.find('ul',class_='item-features')
    ItemID,Title,Shipping,Image_Url,Branding,Model,DirectX,HDMI,DisplayPort,Max_Resolution = "Null","Null","Null","Null","Null","Null","Null","Null","Null","Null"
    Item_rating,Num_rate,Price = 0,0,0
    for Data_fea in Data_feas:
        try:
            li_Data_fea = Data_fea.find('strong')
            if li_Data_fea.text.strip() == "Max Resolution:" :
                Max_Resolution = li_Data_fea.next_sibling.strip()

            elif li_Data_fea.text.strip() == "DisplayPort:" :
                DisplayPort = li_Data_fea.next_sibling.strip()

            elif li_Data_fea.text.strip() == "HDMI:" :
                HDMI = li_Data_fea.next_sibling.strip()

            elif li_Data_fea.text.strip() == "Model #:" :
                Model = li_Data_fea.next_sibling.strip()

            elif li_Data_fea.text.strip() == "Item #:" :
                ItemID = li_Data_fea.next_sibling.strip()   
                            
            elif li_Data_fea.text.strip() == "DirectX:" :
                DirectX = li_Data_fea.next_sibling.strip()

        except:
            pass

    item_infos = Spec.find_all("div",class_ = "item-branding")
    for item_info in item_infos:
        try:
            Brands = item_info.find_all('a',class_="item-brand")
            for Brand in Brands:
                Branding = Brand.find('img')['alt']
            Data_Item_ratings = item_info.find_all("a",class_ = "item-rating")
            for Data_Item_rating in Data_Item_ratings:
                Item_rating = float(regex("rated"," out",Data_Item_rating.find("i")["aria-label"]))
                Num_rate = int(Data_Item_rating.find("span",class_ = "item-rating-num").text.replace("(","").replace(")",""))
        except:
            pass
    try:
        Title = Spec.find("span",class_ = "item-open-box-italic").next_sibling.strip()
        Price =  float(re.findall("\d+\.\d+",Spec.find('li',attrs={'class':'price-current'}).text.strip().replace(",",""))[0])
        Shipping = Spec.find('li',class_='price-ship').text
        Image_Url = Spec.find("a",class_ = "item-img").find("img")['src']
    except:
        pass
    if ItemID == "Null":
        ItemID = id  

    row = {
            "ItemID" : ItemID,
            "Title" : Title,
            "Branding" : Branding,
            "Rating" : Item_rating,
            "Num_rating" : Num_rate,
            "Price" : Price,
            "Shipping" : Shipping,
            "Image_Url" : Image_Url,
            "Spectification": {
                            "Max_Resolution" : Max_Resolution,
                            "DisplayPort" : DisplayPort ,
                            "HDMI" : HDMI ,
                            "DirectX" : DirectX,
                            "Model" : Model}}
    
    # print(row)    
    return row,count


def main():
    count=0
    for Page_id in range(1,100):
        print("here")
        PAGE = f"https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-{Page_id}?Tid=7709"
        print(f"href: {PAGE}")
        result = requests.get(PAGE)  
        assert result.status_code == 200, f"Got Status code {result.status_code}\which isn't a success"
        source = result.text
        soup = BeautifulSoup(source, 'html.parser')
        Specs = soup.find_all('div', class_='item-cell')
        rows =[]
        for Spec in Specs:      
            row,count = extract_data(Spec,count)
            rows.append(row)
        Mysql(rows) 


if __name__== "__main__":
    main()
            
