# rocknest-backend
The project is a Django-based e-commerce website that sells sculptures. It provides a RESTful API that allows customers to browse and purchase sculptures, and administrators to manage the inventory, orders, and customers.


# Technologies Used
The project is built using Django, a Python-based web framework that provides a high-level, modular architecture for building web applications. The backend uses Django's Object-Relational Mapping (ORM) to interface with the database, and the Django Rest Framework (DRF) to build the REST API.

# API Documentation
The REST API is fully documented using the OpenAPI specification (formerly known as Swagger). The documentation provides detailed descriptions of all the available endpoints, request and response schemas, and sample responses.

# Installation and Usage
To install and run the project, follow these steps:

Clone the repository from GitHub.
Create a virtual environment and activate it.
Install the required dependencies from the requirements.txt file.
Set up the database and apply the migrations using the python manage.py makemigrations then python manage.py migrate script.
Start the development server using the python manage.py runserver script.

access the api documentaion through this link : http://127.0.0.1:8000/swagger/

# Conclusion
In conclusion, the project is a Django-based e-commerce website selling sculptures, with a focus on its backend and REST API. It provides a range of features for browsing, searching, purchasing, managing inventory, orders, and customers. The REST API is fully documented using the OpenAPI specification, making it easy to integrate with other applications or build custom frontends.