# Handoff to Heba: frontend

Verified local service addresses from the existing runtime validation:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- MLflow: `http://localhost:5000`
- PostgreSQL: `localhost:5432`

The frontend must call the backend API and must not connect directly to
PostgreSQL or MLflow. Please confirm the API base URL variable, Docker service
hostname, development port, API integration expectations, and display of
source/citation metadata returned with answers.
