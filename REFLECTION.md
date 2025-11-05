# Reflection - Assignment 13: JWT Authentication

## What I Learned

In this assignment, I learned how JWT authentication works. When a user registers and logs in, the server generates a JWT token that proves they are authenticated. This token is stored in the browser and sent with each request.

I also learned about password security. Using bcrypt, passwords are hashed before storing in the database. This means even if the database is hacked, the passwords remain secure because they're not stored in plaintext.

## Challenges I Faced

### Challenge 1: Database Port Already in Use
When I first started Docker, I got an error that port 5432 was already in use. I fixed this by changing the Docker port to 5433 in docker-compose.yml and updating the database URL.

### Challenge 2: Tables Not Created
The database tables weren't being created automatically. I had to run the database initialization script manually:
```
docker-compose exec web python -m app.database_init
```

After running this, all tables were created and the app started working.

### Challenge 3: Testing the Full Flow
I tested the registration and login step by step. First I used curl commands to test the API endpoints. This confirmed the backend was working. Then I tested the HTML forms in the browser. After registering and logging in, I could see the dashboard with all calculations.

## How I Solved These Problems

1. Changed the database port configuration
2. Ran the database initialization script
3. Tested with curl first, then tested in the browser
4. Verified everything worked end-to-end

## Testing Process

1. Started all Docker containers
2. Registered a new user via curl
3. Logged in via curl and got JWT token
4. Opened register page in browser
5. Filled out form and registered successfully
6. Logged in through browser
7. Saw dashboard with calculations
8. Ran all 99 tests with pytest

## What I Would Improve

- I should have checked Docker logs earlier when errors occurred
- Testing with curl first saved me time - I'll do this first next time
- Better documentation of the setup process would have helped

## Conclusion

This assignment taught me that building a complete authentication system requires testing every part carefully. From API endpoints to frontend forms to database setup, everything must work together. The key was testing step-by-step to find problems quickly. I now understand how professional web applications handle user authentication and security.
