require("dotenv").config();

const chai = require("chai");
const chaiHttp = require("chai-http");
const expect = chai.expect;

chai.use(chaiHttp);

const REQUEST_DELAY = Number.parseInt(process.env.REQUEST_DELAY);
const REGION = process.env.REGION;
const SERVER_URL = process.env.SERVER_URL;
const STAGE = process.env.STAGE;
const USER_EMAIL = process.env.USER_EMAIL;
const USER_PASSWORD = process.env.USER_PASSWORD;

const PREFIX = `/${STAGE}/api/v1/auth`;

let token = null;
let roleId = null;

describe("API endpoints /api/v1/*", () => {
  it(`${PREFIX}/welcome: should get a public key`, (done) => {
    chai
      .request(SERVER_URL)
      .get(`${PREFIX}/welcome`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .end((err, res) => {
        expect(res).to.have.status(200);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "0");
        expect(res.body).to.have.property("msg", "ok");
        expect(res.body.data).to.have.property("pubkey").that.is.a("string");
        done();
      });
  });

  it(`${PREFIX}/login: login success`, (done) => {
    chai
      .request(SERVER_URL)
      .post(`${PREFIX}/login`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .send({
        email: USER_EMAIL,
        pubkey: "the-pubkey",
        meta: `{"pass":"${USER_PASSWORD}"}`,
        prefetch: 3,
      })
      .end((err, res) => {
        expect(res).to.have.status(201);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "0");
        expect(res.body).to.have.property("msg", "ok");

        // check data
        expect(res.body).to.have.property("data").that.is.an("object");

        // check auth
        const auth = res.body.data.auth;
        expect(auth).to.be.an("object");
        expect(auth).to.have.property("email", USER_EMAIL);
        expect(auth).to.have.property("role", "teacher");
        expect(auth).to.have.property("role_id").that.is.a("number");
        expect(auth).to.have.property("token").that.is.a("string");
        expect(auth).to.have.property("region", REGION);
        expect(auth).to.have.property("current_region", REGION);
        expect(auth).to.have.property("online", true);
        expect(auth).to.have.property("created_at").that.is.a("number");
        token = "Bearer " + auth.token;
        roleId = auth.role_id;

        // check match
        const match = res.body.data.match;
        expect(match).to.be.an("object");
        expect(match).to.have.property("brief_jobs").that.is.an("array");
        expect(match).to.have.property("followed").that.is.an("array");
        expect(match).to.have.property("contact").that.is.an("array");

        done();
      });
  });

  it(`${PREFIX}/login: error password`, (done) => {
    chai
      .request(SERVER_URL)
      .post(`${PREFIX}/login`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .send({
        email: USER_EMAIL,
        pubkey: "the-pubkey",
        meta: '{"pass":"password2"}',
        prefetch: 3,
      })
      .end((err, res) => {
        expect(res).to.have.status(401);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "40100");
        expect(res.body).to.have.property("msg", "error_password");

        // check data
        expect(res.body).to.have.property("data").that.is.not.an("object");

        done();
      });
  });

  it(`${PREFIX}/password/{role_id}/update: no token error`, (done) => {
    chai
      .request(SERVER_URL)
      .put(`${PREFIX}/password/${roleId}/update`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .send({
        register_email: USER_EMAIL,
        password1: "string1",
        password2: "string2",
        origin_password: USER_PASSWORD,
      })
      .end((err, res) => {
        expect(res).to.have.status(403);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("detail").that.is.an("string");

        done();
      });
  });

  it(`${PREFIX}/password/{role_id}/update: access denied (invalid role_id)`, (done) => {
    const invalidRoleId = 123;
    chai
      .request(SERVER_URL)
      .put(`${PREFIX}/password/${invalidRoleId}/update`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .set("Authorization", token)
      .send({
        register_email: USER_EMAIL,
        password1: "string1",
        password2: "string2",
        origin_password: USER_PASSWORD,
      })
      .end((err, res) => {
        expect(res).to.have.status(401);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "40100");
        expect(res.body).to.have.property("msg", "access denied");

        // check data
        expect(res.body).to.have.property("data").that.is.not.an("object");

        done();
      });
  });

  it(`${PREFIX}/password/{role_id}/update: access denied (invalid token)`, (done) => {
    chai
      .request(SERVER_URL)
      .put(`${PREFIX}/password/${roleId}/update`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .set("Authorization", "invalid-token")
      .send({
        register_email: USER_EMAIL,
        password1: "string",
        password2: "string",
        origin_password: USER_PASSWORD,
      })
      .end((err, res) => {
        expect(res).to.have.status(403);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("detail", "Not authenticated");

        done();
      });
  });

  it(`${PREFIX}/password/{role_id}/update: Password not match`, (done) => {
    chai
      .request(SERVER_URL)
      .put(`${PREFIX}/password/${roleId}/update`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .set("Authorization", token)
      .send({
        register_email: USER_EMAIL,
        password1: "string1",
        password2: "string2",
        origin_password: USER_PASSWORD,
      })
      .end((err, res) => {
        expect(res).to.have.status(400);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "40000");
        expect(res.body).to.have.property("msg", "passwords do not match");

        // check data
        expect(res.body).to.have.property("data").that.is.not.an("object");

        done();
      });
  });

  it(`${PREFIX}/password/{role_id}/update: Invalid Password`, (done) => {
    chai
      .request(SERVER_URL)
      .put(`${PREFIX}/password/${roleId}/update`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .set("Authorization", token)
      .send({
        register_email: USER_EMAIL,
        password1: "string",
        password2: "string",
        origin_password: "invalid-password",
      })
      .end((err, res) => {
        expect(res).to.have.status(403);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "40300");
        expect(res.body).to.have.property("msg", "Invalid Password");

        // check data
        expect(res.body).to.have.property("data").that.is.not.an("object");

        done();
      });
  });

  it(`${PREFIX}/password/{role_id}/update: update success`, (done) => {
    chai
      .request(SERVER_URL)
      .put(`${PREFIX}/password/${roleId}/update`)
      .timeout(REQUEST_DELAY)
      .set("current-region", REGION)
      .set("Authorization", token)
      .send({
        register_email: USER_EMAIL,
        password1: USER_PASSWORD,
        password2: USER_PASSWORD,
        origin_password: USER_PASSWORD,
      })
      .end((err, res) => {
        expect(res).to.have.status(200);
        expect(res.body).to.be.an("object");
        expect(res.body).to.have.property("code", "0");
        expect(res.body).to.have.property("msg", "update success");

        // check data
        expect(res.body).to.have.property("data").that.is.not.an("object");

        done();
      });
  });
});
