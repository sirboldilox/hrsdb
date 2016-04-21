Data Types
-----------

Definitions for the types of data stored in the database.

Patient records
~~~~~~~~~~~~~~~

Basic data about individual patients:

+-------+----------------+-----------------------+
| Type  | Name           | Description           |
+-------+----------------+-----------------------+
| int   | id             | Unique identifier     |
| str   | First name     | Patient first name    |
| str   | Second name    | Patient last name     |
| int   | Gender         | Gender M(0) F(1)      |
| d/t   | Date of birth  | DD/MM/YYYY            |
+-------+----------------+-----------------------+

Biometric Types
~~~~~~~~~~~~~~~

Static biometric types for sorting biometric records

+-------+----------------+-----------------------+
| Type  | Name           | Description           |
+-------+----------------+-----------------------+
| int   | id             | Unique identifier     |
| name  |
| units | blood pressure |                       |
+-------+----------------+-----------------------+

Biometric readings
~~~~~~~~~~~~~~~~~~

Data from biometric readings

+-------+----------------+-----------------------+
| Type  | Name           | Description           |
+-------+----------------+-----------------------+
| int   | height         | Height in meters      |
| int   | weight         | Weigh in Kilograms    |
|       | blood pressure |                       |
| d/t   | timestamp      | Timestamp of readings |
+-------+----------------+-----------------------+

ECG readings
~~~~~~~~~~~~

+-------+----------------+-----------------------+
| Type  | Name           | Description           |
+-------+----------------+-----------------------+
| int   | Sampling rate  | Frequency in Hertz    |
| int   | Sample count   | Number of samples     |
| str   | Path           | Path to the data file |
+-------+----------------+-----------------------+
