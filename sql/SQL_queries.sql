-- =====================================================================
-- SALES ANALYTICS & BUSINESS INTELLIGENCE - SQL QUERY COLLECTION
-- Database: SQLite (sales.db)
-- Table: sales
-- Description: 22 Production-Ready Business Intelligence & Analytical Queries
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: EXECUTIVE KPI SUMMARY
-- Business Question: What are the overarching business metrics (Total Revenue, Total Profit, Profit Margin, Orders, Customers)?
-- Concepts: SELECT, Aggregate Functions (SUM, COUNT, ROUND), Arithmetic Expressions
-- ---------------------------------------------------------------------
SELECT 
    ROUND(SUM(Sales), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Overall_Profit_Margin_Pct,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    COUNT(DISTINCT Customer_ID) AS Total_Unique_Customers,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(Sales) / COUNT(DISTINCT Order_ID), 2) AS Average_Order_Value
FROM sales;


-- ---------------------------------------------------------------------
-- QUERY 2: REGIONAL REVENUE AND PROFITABILITY
-- Business Question: Which region generates the highest revenue and net profit?
-- Concepts: GROUP BY, ORDER BY, Aggregations, Percentage of Total
-- ---------------------------------------------------------------------
SELECT 
    Region,
    ROUND(SUM(Sales), 2) AS Regional_Sales,
    ROUND(SUM(Profit), 2) AS Regional_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Profit_Margin_Pct,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    ROUND(AVG(Discount) * 100, 2) AS Avg_Discount_Pct
FROM sales
GROUP BY Region
ORDER BY Regional_Sales DESC;


-- ---------------------------------------------------------------------
-- QUERY 3: CATEGORY PROFITABILITY AND MARGIN COMPARISON
-- Business Question: Which category generates the highest profit, and how do margins compare?
-- Concepts: GROUP BY, ORDER BY, SUM, ROUND
-- ---------------------------------------------------------------------
SELECT 
    Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Profit_Margin_Pct,
    SUM(Quantity) AS Total_Quantity_Sold,
    ROUND(AVG(Discount) * 100, 2) AS Avg_Discount_Pct
FROM sales
GROUP BY Category
ORDER BY Total_Profit DESC;


-- ---------------------------------------------------------------------
-- QUERY 4: SUB-CATEGORY PROFIT LEAKAGE ANALYSIS
-- Business Question: Which sub-categories are losing money despite high revenue?
-- Concepts: GROUP BY, HAVING, ORDER BY, CASE WHEN
-- ---------------------------------------------------------------------
SELECT 
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2) AS SubCat_Sales,
    ROUND(SUM(Profit), 2) AS SubCat_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Margin_Pct,
    CASE 
        WHEN SUM(Profit) < 0 THEN 'Loss Maker (Critical)'
        WHEN (SUM(Profit) / SUM(Sales)) < 0.10 THEN 'Low Margin (Warning)'
        ELSE 'Healthy Margin'
    END AS Profitability_Status
FROM sales
GROUP BY Category, Sub_Category
ORDER BY SubCat_Profit ASC;


-- ---------------------------------------------------------------------
-- QUERY 5: TOP 10 HIGH-VALUE CUSTOMERS BY REVENUE
-- Business Question: Who are our top 10 most valuable customers by lifetime sales?
-- Concepts: GROUP BY, ORDER BY DESC, LIMIT, Aggregation
-- ---------------------------------------------------------------------
SELECT 
    Customer_ID,
    Customer_Name,
    Segment,
    ROUND(SUM(Sales), 2) AS Lifetime_Spend,
    ROUND(SUM(Profit), 2) AS Lifetime_Profit,
    COUNT(DISTINCT Order_ID) AS Order_Count,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Customer_Margin_Pct
FROM sales
GROUP BY Customer_ID, Customer_Name, Segment
ORDER BY Lifetime_Spend DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- QUERY 6: TOP 10 BEST-SELLING PRODUCTS BY REVENUE
-- Business Question: Which 10 products generate the highest gross revenue?
-- Concepts: GROUP BY, ORDER BY DESC, LIMIT
-- ---------------------------------------------------------------------
SELECT 
    Product_ID,
    Product_Name,
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    SUM(Quantity) AS Units_Sold
FROM sales
GROUP BY Product_ID, Product_Name, Category, Sub_Category
ORDER BY Total_Revenue DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- QUERY 7: TOP 10 LOSS-MAKING PRODUCTS (BOTTOM PRODUCTS)
-- Business Question: Which 10 products are generating the highest cumulative financial loss?
-- Concepts: WHERE clause filter, GROUP BY, ORDER BY ASC, LIMIT
-- ---------------------------------------------------------------------
SELECT 
    Product_ID,
    Product_Name,
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Loss,
    SUM(Quantity) AS Total_Quantity,
    ROUND(AVG(Discount) * 100, 2) AS Avg_Discount_Pct
FROM sales
GROUP BY Product_ID, Product_Name, Category, Sub_Category
HAVING SUM(Profit) < 0
ORDER BY Total_Loss ASC
LIMIT 10;


-- ---------------------------------------------------------------------
-- QUERY 8: MONTHLY REVENUE AND PROFIT TRENDS
-- Business Question: What is the monthly revenue, profit, and order cadence over time?
-- Concepts: GROUP BY Year-Month, Aggregate functions, Temporal ordering
-- ---------------------------------------------------------------------
SELECT 
    Order_Year_Month,
    ROUND(SUM(Sales), 2) AS Monthly_Revenue,
    ROUND(SUM(Profit), 2) AS Monthly_Profit,
    COUNT(DISTINCT Order_ID) AS Monthly_Orders,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Monthly_Margin_Pct
FROM sales
GROUP BY Order_Year_Month
ORDER BY Order_Year_Month ASC;


-- ---------------------------------------------------------------------
-- QUERY 9: AVERAGE ORDER VALUE (AOV) ACROSS CUSTOMER SEGMENTS
-- Business Question: Which customer segment yields the highest AOV and profitability?
-- Concepts: GROUP BY, Aggregate expressions, Division, Ordering
-- ---------------------------------------------------------------------
SELECT 
    Segment,
    COUNT(DISTINCT Customer_ID) AS Customer_Count,
    COUNT(DISTINCT Order_ID) AS Order_Count,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Sales) / COUNT(DISTINCT Order_ID), 2) AS Average_Order_Value,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Profit_Margin_Pct
FROM sales
GROUP BY Segment
ORDER BY Total_Sales DESC;


-- ---------------------------------------------------------------------
-- QUERY 10: DISCOUNT IMPACT ON MARGINS (DISCOUNT SENSITIVITY)
-- Business Question: How does discounting intensity correlate with profitability?
-- Concepts: CASE WHEN, GROUP BY, Aggregate metrics, Margin analysis
-- ---------------------------------------------------------------------
SELECT 
    CASE 
        WHEN Discount = 0 THEN '0% (Full Price)'
        WHEN Discount > 0 AND Discount <= 0.20 THEN '1% - 20% (Low Discount)'
        WHEN Discount > 0.20 AND Discount <= 0.40 THEN '21% - 40% (Moderate Discount)'
        ELSE '> 40% (Deep Discount)'
    END AS Discount_Tier,
    COUNT(*) AS Transaction_Count,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Realized_Margin_Pct,
    ROUND(AVG(Sales), 2) AS Avg_Order_Line_Sales
FROM sales
GROUP BY Discount_Tier
ORDER BY Realized_Margin_Pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 11: WEAK-PERFORMING STATES BY NET PROFIT
-- Business Question: Which states generate net financial losses for the business?
-- Concepts: GROUP BY, HAVING, ORDER BY ASC
-- ---------------------------------------------------------------------
SELECT 
    State,
    Region,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Net_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Margin_Pct,
    COUNT(DISTINCT Order_ID) AS Orders,
    ROUND(AVG(Discount) * 100, 2) AS Avg_Discount_Pct
FROM sales
GROUP BY State, Region
HAVING Net_Profit < 0
ORDER BY Net_Profit ASC;


-- ---------------------------------------------------------------------
-- QUERY 12: SHIPPING MODE EFFICIENCY AND SPEED
-- Business Question: What is the average shipping turnaround and order distribution by shipping method?
-- Concepts: GROUP BY, AVG, MIN, MAX, COUNT
-- ---------------------------------------------------------------------
SELECT 
    Ship_Mode,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    ROUND(AVG(Shipping_Days), 2) AS Avg_Shipping_Days,
    MIN(Shipping_Days) AS Min_Days,
    MAX(Shipping_Days) AS Max_Days,
    ROUND(SUM(Sales), 2) AS Total_Revenue,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM sales
GROUP BY Ship_Mode
ORDER BY Total_Orders DESC;


-- ---------------------------------------------------------------------
-- QUERY 13: YEAR-OVER-YEAR (YoY) ANNUAL GROWTH ANALYSIS
-- Business Question: How has revenue and profit evolved from year to year?
-- Concepts: Common Table Expressions (CTE), Self-Join or Lag-style logic
-- ---------------------------------------------------------------------
WITH AnnualMetrics AS (
    SELECT 
        Order_Year,
        ROUND(SUM(Sales), 2) AS Annual_Sales,
        ROUND(SUM(Profit), 2) AS Annual_Profit,
        COUNT(DISTINCT Order_ID) AS Annual_Orders
    FROM sales
    GROUP BY Order_Year
)
SELECT 
    curr.Order_Year,
    curr.Annual_Sales,
    prev.Annual_Sales AS Prev_Year_Sales,
    ROUND(((curr.Annual_Sales - prev.Annual_Sales) / prev.Annual_Sales) * 100, 2) AS Sales_YoY_Growth_Pct,
    curr.Annual_Profit,
    prev.Annual_Profit AS Prev_Year_Profit,
    ROUND(((curr.Annual_Profit - prev.Annual_Profit) / prev.Annual_Profit) * 100, 2) AS Profit_YoY_Growth_Pct,
    curr.Annual_Orders
FROM AnnualMetrics curr
LEFT JOIN AnnualMetrics prev ON curr.Order_Year = prev.Order_Year + 1
ORDER BY curr.Order_Year ASC;


-- ---------------------------------------------------------------------
-- QUERY 14: CUSTOMER REPURCHASE FREQUENCY & RETENTION
-- Business Question: How many customers are single-order vs repeat purchasers?
-- Concepts: CTE, Subquery, GROUP BY, CASE WHEN, Proportion
-- ---------------------------------------------------------------------
WITH CustomerOrderCounts AS (
    SELECT 
        Customer_ID,
        Customer_Name,
        COUNT(DISTINCT Order_ID) AS Lifetime_Orders,
        SUM(Sales) AS Total_Spent
    FROM sales
    GROUP BY Customer_ID, Customer_Name
)
SELECT 
    CASE 
        WHEN Lifetime_Orders = 1 THEN '1. One-Time Buyer'
        WHEN Lifetime_Orders BETWEEN 2 AND 4 THEN '2. Repeat Buyer (2-4 Orders)'
        WHEN Lifetime_Orders BETWEEN 5 AND 9 THEN '3. Frequent Buyer (5-9 Orders)'
        ELSE '4. VIP / Power Buyer (10+ Orders)'
    END AS Loyalty_Tier,
    COUNT(Customer_ID) AS Customer_Count,
    ROUND(SUM(Total_Spent), 2) AS Total_Revenue,
    ROUND(AVG(Total_Spent), 2) AS Avg_Customer_Spend
FROM CustomerOrderCounts
GROUP BY Loyalty_Tier
ORDER BY Loyalty_Tier ASC;


-- ---------------------------------------------------------------------
-- QUERY 15: WINDOW FUNCTION - RANKING PRODUCTS WITHIN EACH CATEGORY
-- Business Question: What are the top 3 revenue-generating products inside each category?
-- Concepts: CTE, Window Function DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)
-- ---------------------------------------------------------------------
WITH RankedProducts AS (
    SELECT 
        Category,
        Sub_Category,
        Product_Name,
        ROUND(SUM(Sales), 2) AS Product_Sales,
        ROUND(SUM(Profit), 2) AS Product_Profit,
        DENSE_RANK() OVER (PARTITION BY Category ORDER BY SUM(Sales) DESC) AS Category_Rank
    FROM sales
    GROUP BY Category, Sub_Category, Product_Name
)
SELECT 
    Category,
    Category_Rank,
    Sub_Category,
    Product_Name,
    Product_Sales,
    Product_Profit
FROM RankedProducts
WHERE Category_Rank <= 3
ORDER BY Category, Category_Rank;


-- ---------------------------------------------------------------------
-- QUERY 16: WINDOW FUNCTION - RUNNING CUMULATIVE REVENUE OVER TIME
-- Business Question: What is the month-by-month cumulative running total of revenue?
-- Concepts: CTE, Window Function SUM(...) OVER (ORDER BY ...)
-- ---------------------------------------------------------------------
WITH MonthlyTotals AS (
    SELECT 
        Order_Year_Month,
        ROUND(SUM(Sales), 2) AS Monthly_Sales,
        ROUND(SUM(Profit), 2) AS Monthly_Profit
    FROM sales
    GROUP BY Order_Year_Month
)
SELECT 
    Order_Year_Month,
    Monthly_Sales,
    ROUND(SUM(Monthly_Sales) OVER (ORDER BY Order_Year_Month ASC), 2) AS Cumulative_Running_Revenue,
    Monthly_Profit,
    ROUND(SUM(Monthly_Profit) OVER (ORDER BY Order_Year_Month ASC), 2) AS Cumulative_Running_Profit
FROM MonthlyTotals
ORDER BY Order_Year_Month ASC;


-- ---------------------------------------------------------------------
-- QUERY 17: WINDOW FUNCTION - CUSTOMER ORDER SEQUENCE & RECENCY
-- Business Question: What is the sequence number for every order placed by customers?
-- Concepts: Window Function ROW_NUMBER() OVER (PARTITION BY Customer_ID ORDER BY Order_Date)
-- ---------------------------------------------------------------------
SELECT 
    Order_ID,
    Customer_ID,
    Customer_Name,
    Order_Date,
    ROUND(SUM(Sales), 2) AS Order_Value,
    ROW_NUMBER() OVER (PARTITION BY Customer_ID ORDER BY Order_Date ASC, Order_ID ASC) AS Order_Sequence_Num
FROM sales
GROUP BY Order_ID, Customer_ID, Customer_Name, Order_Date
ORDER BY Customer_ID, Order_Sequence_Num
LIMIT 20;


-- ---------------------------------------------------------------------
-- QUERY 18: CTE - ORDERS WITH VALUE SIGNIFICANTLY ABOVE OVERALL AVERAGE
-- Business Question: Which orders exceeded 3x the store-wide average order value?
-- Concepts: Multi-Level CTE, Scalar subquery aggregation, Filtering
-- ---------------------------------------------------------------------
WITH OrderAggregates AS (
    SELECT 
        Order_ID,
        Customer_Name,
        City,
        State,
        Region,
        ROUND(SUM(Sales), 2) AS Order_Total,
        ROUND(SUM(Profit), 2) AS Order_Profit
    FROM sales
    GROUP BY Order_ID, Customer_Name, City, State, Region
),
StoreBenchmark AS (
    SELECT AVG(Order_Total) AS Benchmark_AOV FROM OrderAggregates
)
SELECT 
    oa.Order_ID,
    oa.Customer_Name,
    oa.City,
    oa.State,
    oa.Region,
    oa.Order_Total,
    oa.Order_Profit,
    ROUND(sb.Benchmark_AOV, 2) AS Avg_Benchmark_AOV,
    ROUND(oa.Order_Total / sb.Benchmark_AOV, 2) AS Multiple_Of_Average
FROM OrderAggregates oa
CROSS JOIN StoreBenchmark sb
WHERE oa.Order_Total >= (3 * sb.Benchmark_AOV)
ORDER BY oa.Order_Total DESC
LIMIT 15;


-- ---------------------------------------------------------------------
-- QUERY 19: REGION X SEGMENT PERFORMANCE MATRIX
-- Business Question: How does each customer segment perform across each geographic territory?
-- Concepts: Multi-column GROUP BY, Aggregations, Cross-dimensional analysis
-- ---------------------------------------------------------------------
SELECT 
    Region,
    Segment,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100, 2) AS Margin_Pct
FROM sales
GROUP BY Region, Segment
ORDER BY Region, Total_Sales DESC;


-- ---------------------------------------------------------------------
-- QUERY 20: LOSS TRANSACTION FREQUENCY PER CATEGORY & SUB-CATEGORY
-- Business Question: What percentage of individual transactions result in negative profit?
-- Concepts: CASE WHEN inside SUM, Ratio calculation, HAVING, ORDER BY
-- ---------------------------------------------------------------------
SELECT 
    Category,
    Sub_Category,
    COUNT(*) AS Total_Transactions,
    SUM(CASE WHEN Profit < 0 THEN 1 ELSE 0 END) AS Loss_Transactions,
    ROUND((CAST(SUM(CASE WHEN Profit < 0 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100, 2) AS Loss_Rate_Pct,
    ROUND(SUM(CASE WHEN Profit < 0 THEN Profit ELSE 0 END), 2) AS Gross_Loss_Amount,
    ROUND(SUM(CASE WHEN Profit >= 0 THEN Profit ELSE 0 END), 2) AS Gross_Gain_Amount,
    ROUND(SUM(Profit), 2) AS Net_Profit
FROM sales
GROUP BY Category, Sub_Category
ORDER BY Loss_Rate_Pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 21: TOP PERFORMING PRODUCT PER SUB-CATEGORY
-- Business Question: What is the #1 single most profitable item in every sub-category?
-- Concepts: CTE, Window Function RANK() OVER (PARTITION BY ... ORDER BY ...)
-- ---------------------------------------------------------------------
WITH RankedSubcatProducts AS (
    SELECT 
        Category,
        Sub_Category,
        Product_Name,
        ROUND(SUM(Profit), 2) AS Net_Product_Profit,
        ROUND(SUM(Sales), 2) AS Net_Product_Sales,
        RANK() OVER (PARTITION BY Sub_Category ORDER BY SUM(Profit) DESC) AS Subcat_Profit_Rank
    FROM sales
    GROUP BY Category, Sub_Category, Product_Name
)
SELECT 
    Category,
    Sub_Category,
    Product_Name,
    Net_Product_Sales,
    Net_Product_Profit
FROM RankedSubcatProducts
WHERE Subcat_Profit_Rank = 1
ORDER BY Category, Sub_Category;


-- ---------------------------------------------------------------------
-- QUERY 22: INNER JOIN & CTE - HIGH-VALUE HIGH-PROFIT CUSTOMERS
-- Business Question: Which top spenders also deliver consistently high profit margins (>20%)?
-- Concepts: Inner Join between CTEs, Filtering, Margin criteria
-- ---------------------------------------------------------------------
WITH TopSpenders AS (
    SELECT 
        Customer_ID,
        Customer_Name,
        Segment,
        ROUND(SUM(Sales), 2) AS Total_Sales,
        ROUND(SUM(Profit), 2) AS Total_Profit
    FROM sales
    GROUP BY Customer_ID, Customer_Name, Segment
    HAVING SUM(Sales) > 5000
),
HighMarginSpenders AS (
    SELECT 
        Customer_ID,
        ROUND((Total_Profit / Total_Sales) * 100, 2) AS Margin_Pct
    FROM TopSpenders
    WHERE (Total_Profit / Total_Sales) >= 0.20
)
SELECT 
    ts.Customer_ID,
    ts.Customer_Name,
    ts.Segment,
    ts.Total_Sales,
    ts.Total_Profit,
    hm.Margin_Pct
FROM TopSpenders ts
INNER JOIN HighMarginSpenders hm ON ts.Customer_ID = hm.Customer_ID
ORDER BY ts.Total_Profit DESC;
