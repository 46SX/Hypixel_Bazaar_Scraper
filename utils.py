from scraper import get_data


def get_item_data(item, data):
    item_data = data[item]
    quick_data = item_data["quick_status"]
    sell_sum = item_data["sell_summary"]
    buy_sum = item_data["buy_summary"]

    def average(sum_data):
        total_cost = sum(listing["pricePerUnit"] * listing["amount"] for listing in sum_data)
        total_amount = sum(listing["amount"] for listing in sum_data)
        return total_cost / total_amount if total_amount > 0 else 0

    average_sell_price = average(sell_sum)
    average_buy_price = average(buy_sum)
    spread_percent = ((average_buy_price - average_sell_price) / average_sell_price) * 100 if average_sell_price > 0 else 0

    profit_margin = quick_data["buyPrice"] - quick_data["sellPrice"]
    profit_percent = profit_margin / quick_data["sellPrice"] * 100
    average_sold_each_day = quick_data["sellMovingWeek"] / 7
    average_bought_each_day = quick_data["buyMovingWeek"] / 7
    order_density = quick_data["buyOrders"] + quick_data["sellOrders"]
    buy_to_sell_ratio = quick_data["buyVolume"] / quick_data["sellVolume"]
    
    return {
        # -----------Normal-Data----------- # 
        "buy_price" : round(quick_data["buyPrice"],2),   # highest buy order (instant sell price)
        "sell_price" : round(quick_data["sellPrice"],2), # lowest sell offer (instant buy price)
        "volume_of_sellorders": round(quick_data["sellVolume"],2), #amount up for sale
        "volume_of_buyorders" : round(quick_data["buyVolume"],2), #amount up for purchase

        # ----------Enchaned-Data---------- #
        "profit_margin" : round(profit_margin,2), #Diffrence between lowest sell order and highest buy order
        "profit_percent" : round(profit_percent,2), #Profit_margin but in percent
        "average_sell_price" : round(average_sell_price,2), # average sell price
        "average_buy_price" : round(average_buy_price,2), # average buy price 
        "average_sold_each_day" : round(average_sold_each_day,2), #Average amount sold every day, calculated by dividing amount sold every week with 7
        "average_bought_each_day" : round(average_bought_each_day,2), #Same thing but for the average bought every day ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        "order_density" : round(order_density,2), #Total activity of a item (buyOrders + sellOrders)
        "spread_percent" : round(spread_percent,2), # Diffrence between average buy and average sell in percent. Better than quick_status margin for finding flips
        "buy_to_sell_ratio" : round(buy_to_sell_ratio,2) # buyVolume/sellVolume, Basically demand and supply =)
    }






