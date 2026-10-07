package com.fudn.inventoryservice;

import io.restassured.RestAssured;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.containers.MySQLContainer;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class SwaggerIntegrationTest {

    @ServiceConnection
    static MySQLContainer mySQLContainer = new MySQLContainer("mysql:8.3.0");

    static {
        mySQLContainer.start();
    }

    @LocalServerPort
    private Integer port;

    @BeforeEach
    void setup() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = port;
    }

    @Test
    void swaggerUiShouldBeAccessible() {
        RestAssured.given()
                .when()
                .get("/swagger-ui.html")
                .then()
                .statusCode(Matchers.isOneOf(200, 302));
    }

    @Test
    void apiDocsShouldReturnJson() {
        RestAssured.given()
                .when()
                .get("/api-docs")
                .then()
                .statusCode(200)
                .body("info.title", equalTo("Inventory Service API"))
                .body("info.version", equalTo("v0.0.1"));
    }

    @Test
    void apiDocsShouldContainInventoryEndpoints() {
        RestAssured.given()
                .when()
                .get("/api-docs")
                .then()
                .statusCode(200)
                .body("paths", notNullValue());
    }
}
