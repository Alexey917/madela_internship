1179. Reformat Department Table

Table: Department

+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| id          | int     |
| revenue     | int     |
| month       | varchar |
+-------------+---------+
In SQL,(id, month) is the primary key of this table.
The table has information about the revenue of each department per month.
The month has values in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].
 

Reformat the table such that there is a department id column and a revenue column for each month.

Return the result table in any order.

The result format is in the following example.

 

Example 1:

Input: 
Department table:
+------+---------+-------+
| id   | revenue | month |
+------+---------+-------+
| 1    | 8000    | Jan   |
| 2    | 9000    | Jan   |
| 3    | 10000   | Feb   |
| 1    | 7000    | Feb   |
| 1    | 6000    | Mar   |
+------+---------+-------+
Output: 
+------+-------------+-------------+-------------+-----+-------------+
| id   | Jan_Revenue | Feb_Revenue | Mar_Revenue | ... | Dec_Revenue |
+------+-------------+-------------+-------------+-----+-------------+
| 1    | 8000        | 7000        | 6000        | ... | null        |
| 2    | 9000        | null        | null        | ... | null        |
| 3    | null        | 10000       | null        | ... | null        |
+------+-------------+-------------+-------------+-----+-------------+
Explanation: The revenue from Apr to Dec is null.
Note that the result table has 13 columns (1 for the department id + 12 for the months).

select id, 
    max(revenue) filter (where month = 'Jan') as Jan_Revenue,
    max(revenue) filter (where month = 'Feb') as Feb_Revenue,
    max(revenue) filter (where month = 'Mar') as Mar_Revenue,
    max(revenue) filter (where month = 'Apr') as Apr_Revenue,
    max(revenue) filter (where month = 'May') as May_Revenue,
    max(revenue) filter (where month = 'Jun') as Jun_Revenue,
    max(revenue) filter (where month = 'Jul') as Jul_Revenue,
    max(revenue) filter (where month = 'Aug') as Aug_Revenue,
    max(revenue) filter (where month = 'Sep') as Sep_Revenue,
    max(revenue) filter (where month = 'Oct') as Oct_Revenue,
    max(revenue) filter (where month = 'Nov') as Nov_Revenue,
    max(revenue) filter (where month = 'Dec') as Dec_Revenue
from department
group by id
order by id