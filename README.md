# Telegram bot alias
[@JustNewInnoBot](https://t.me/JustNewInnoBot)

# Project description

Our idea is to provide service for automatic querying Google Sheets for business insights extraction.

1) User sends query in natural language with link to Google Sheet from which he want to receive business insight
2) Our service downloads spreadsheet in csv format
3) LLM generates query in SQL language based on user message and table schema
4) Service executes query on table and provide results
5) LLM generates concise and accurate report based on the query result and user message and print it to the user

# Datasets used:
1) [https://docs.google.com/spreadsheets/d/1Ucc4-r11InYoK7IGoDLWOtzeuXOwxsnsfD2y0DffXQ4](https://docs.google.com/spreadsheets/d/1Ucc4-r11InYoK7IGoDLWOtzeuXOwxsnsfD2y0DffXQ4)
2) [https://docs.google.com/spreadsheets/d/1AZ1p0PUC1kvEpGcduzpM9-lUjh4FlBeC0KE8eOGfam8](https://docs.google.com/spreadsheets/d/1AZ1p0PUC1kvEpGcduzpM9-lUjh4FlBeC0KE8eOGfam8)

# Plan execution examples
## User:

Which Product was ordered the most based on Quantity Ordered? https://docs.google.com/spreadsheets/d/1AZ1p0PUC1kvEpGcduzpM9-lUjh4FlBeC0KE8eOGfam8

## Reply:

1 : Document id: 
1AZ1p0PUC1kvEpGcduzpM9-lUjh4FlBeC0KE8eOGfam8

2 : Query is executed successfully

3 : Report: 
Based on the provided data, the product that was ordered the most based on Quantity Ordered is:

1. AAA Batteries (4-pack)

Plan status - Completed successfully : Done

![image_1](images/image_1.png)

## User:

what is the average age of employees? https://docs.google.com/spreadsheets/d/1Ucc4-r11InYoK7IGoDLWOtzeuXOwxsnsfD2y0DffXQ4

## Reply:

1 : Document id: 
1Ucc4-r11InYoK7IGoDLWOtzeuXOwxsnsfD2y0DffXQ4

2 : Query is executed successfully

3 : Report: 
The average age of employees is approximately 37.43 years.

Plan status - Completed successfully : Done

![image_2](images/image_2.png)

## User:

What are the highest and lowest Salaries? https://docs.google.com/spreadsheets/d/1Ucc4-r11InYoK7IGoDLWOtzeuXOwxsnsfD2y0DffXQ4

## Reply:

1 : Document id: 
1Ucc4-r11InYoK7IGoDLWOtzeuXOwxsnsfD2y0DffXQ4

2 : Query is executed successfully

3 : Report: 
The highest salary is $250,000.00 and the lowest salary is $350.00.

Plan status - Completed successfully : Done

![image_3](images/image_3.png)

## User:

What are the total Sales for each Month? https://docs.google.com/spreadsheets/d/1AZ1p0PUC1kvEpGcduzpM9-lUjh4FlBeC0KE8eOGfam8

## Reply:

1 : Document id: 
1AZ1p0PUC1kvEpGcduzpM9-lUjh4FlBeC0KE8eOGfam8

2 : Query is executed successfully

3 : Report: 
The total sales for each month are as follows:

1. January: $1,182,225.67
2. February: $2,220,202.42
3. March: $2,807,100.38
4. April: $3,390,670.24
5. May: $3,152,606.75
6. June: $2,577,802.26
7. July: $2,647,775.76
8. August: $2,244,467.88
9. September: $2,097,560.13
10. October: $3,736,726.88
11. November: $3,199,603.20
12. December: $4,613,443.34

Plan status - Completed successfully : Done

![image_4](images/image_4.png)

# Business applications:

1. Business and Management
    - Sales analysis and reporting.
    - KPI and performance tracking.
2. Finance and accounting
    - Automation of calculation of taxes and fees.
    - Income and expense reports.
    - Financial planning and budget analysis.
3. Education
    - Analysis of student performance.
    - Managing schedules and attendance.
    - Evaluation of the effectiveness of educational programs.
4. Production
    - Analysis of the productivity and efficiency of processes.
    - Inventory management of raw materials and finished products.

