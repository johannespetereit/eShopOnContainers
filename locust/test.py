import os
from locustfile import interactive_locust
interactive_locust(r'..\src\Services\Identity\Identity.API\Setup\Users.csv')