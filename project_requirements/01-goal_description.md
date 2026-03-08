# Description

The PhrasalVerbSvc will help users to learn phrasal verbs in English.

# Goals
* The user can practice phrasal verbs for learning or improving english language.

## Functional Requirements

### Application management
* The service must have an initial list of the 100 top used phrasal verbs
    * The admin user can add more phrasal verbs to the application catalog
* Supported language list:
    * English
    * German
* Native language
    * This is the language the end user speaks, this list must include Spanish.
    * Catalog: This is the list of supported languages, add the top 5 more spoken languages in the world
* The service will keep information of the user
    * The user id
    * Native language and Learning languages
    * The selected phrasal verbs from the catalog
        * The user is able to add its own phrasal verbs, there is no restriction
    * The application will keep a record of:
        * How many times each phrasal verb was responded correctly/incorrectly
        * Feedback: Analysis of the detected failure reason, if any


### End user
* The user
    * will choose the target language(s)
    * can select a subset of phrasal verbs from the catalog, this selection must be stored by the application per user
    * can choose a phrasal verb to practice or enable random mode

### Phrasal Verb Exercise Types

#### Writting - Phrasal Verb Exercise

##### Prerequites

* Native and target user language. This is Required.
* Narrow the situation, for instance if the user wants to practice the phrasal verb in the conext of a office, or street. This is Optional

##### Excercise

* The service will generate:
    1. A scenario in native language, with a short description, so the user has a context of the sentence
    2. A sentence in native language, this is the example sentence in native language
    3. A sentence in target language, this sentence is an example of how to use the phrasal verb

##### Answer

* The user will write the sentence in target language using the phrasal verb

##### Evaluation

* The system will evaluate if the sent answer is correct
* It  will return feedback weather correct/incorrect, if the answer was incorrect it must give the correct example.


## Non-Functional Requirements
* The webapi is part of the application in the current solution, the LanguageApp-IdentitySvc is hte identity service for the portal
* Use the current web api project structure and architecture
  * it's possible to suggest improvements but they must be approved by me first
* Use SOLID principles
* Use Clean architecture
* Use current packages when possible
* The language engine is an LLM, it can be ChatGPT/OpenAI or Claude/Anthropic.
  * the application must have support to switch from one to another
* Use MSSQL to store all of the required data
    * Create migration DB using alembic
    * It is possible to implement a different or complementary DB if needed
* Each Request must authenticate the user data and track a request by using a request id
* Each Request must keep track by using the corresponding Azure monitor services as already set in the project.
* Use docker container
  * Generte the docker files for the web api and the database.

## Security Requirements

* The webapi service will grant access to authenticated users
* Endpoints that handle user management or service management actions must be restricted to administrator role (use the one defined in the identity service)
* Other endpoinst must validate the user has phrasalverbs-user role
* Log any security activity in the service using Azure services.