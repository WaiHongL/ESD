# Start from the latest Kong image
FROM kong:latest

# Copy the kong.yml file into the image
COPY ./kongService/kong.yml /etc/kong/kong.yml

# # Set the necessary environment variables
ENV KONG_DATABASE=off 
ENV KONG_DECLARATIVE_CONFIG=/etc/kong/kong.yml
