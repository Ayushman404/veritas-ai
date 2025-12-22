
FROM node:22-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# We can stick to a simple start command here, 
# because docker-compose overrides it anyway.
CMD ["npm", "run", "dev"]