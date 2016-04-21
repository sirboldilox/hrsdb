REST HTTP API
=============

The database can be interfaced with via the HTTP API. The API provides methods for uploading new records and searching for records.

Overview
--------

In general the following HTTP methods are used in the API for the following tasks:

+-----------+-------------------------------------------+
| method    | description                               |
+===========+===========================================+
| get       | fetching records from the database        |
+-----------+-------------------------------------------+
| put       | adding new records to the database        |
+-----------+-------------------------------------------+

The API consists of the following endpoints:

+-----------------------+-----------------------------------------------------------+
| Path                  | Description                                               |
+=======================+===========================================================+
| /patient/<int:id>     | Interfacing with single patient record                    |
+-----------------------+-----------------------------------------------------------+
| /patients             | Fetch all patient records                                 |
+-----------------------+-----------------------------------------------------------+
| /biometric/<int:id>   | Interfacing with a single biometric record                |
+-----------------------+-----------------------------------------------------------+
| /biometrics           | Fetch all biometrics for specific criteria                |
+-----------------------+-----------------------------------------------------------+   
| /ecg                  | Fetch all ecg header information for a specific patient   |
+-----------------------+-----------------------------------------------------------+   
| /ecgdata/<int:id>     | Fetch ecg readings for specific ECG record                |
+-----------------------+-----------------------------------------------------------+   

API reference
-------------

Detailed description of each endpoint

Patient API
~~~~~~~~~~~

API for interfacing with patient records

.. autoclass:: hrsdb.app.PatientAPI
   :members:

.. autoclass:: hrsdb.app.PatientListAPI
   :members:

Biometric API
~~~~~~~~~~~~~

API for interfacing with biometric records

.. autoclass:: hrsdb.app.BiometricAPI
   :members:

.. autoclass:: hrsdb.app.BiometricListAPI
   :members:

ECG API
~~~~~~~

API for interfacing with ECG records and headers

.. autoclass:: hrsdb.app.ECGAPI
   :members:

.. autoclass:: hrsdb.app.ECGDataAPI
   :members:

