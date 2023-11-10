require("dotenv").config();

const chai = require("chai");
const chaiHttp = require("chai-http");
const expect = chai.expect;

chai.use(chaiHttp);

const REQUEST_DELAY = Number.parseInt(process.env.REQUEST_DELAY);
const REGION = process.env.REGION;
const SERVER_URL = process.env.SERVER_URL;
const STAGE = process.env.STAGE;
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
        email: "user@example.com",
        pubkey: "the-pubkey",
        meta: '{"pass":"secret"}',
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
        expect(auth).to.have.property("email", "user@example.com");
        expect(auth).to.have.property("role", "teacher");
        expect(auth).to.have.property("role_id").that.is.a("number");
        expect(auth).to.have.property("token").that.is.a("string");
        expect(auth).to.have.property("region", REGION);
        expect(auth).to.have.property("current_region", REGION);
        expect(auth).to.have.property("socketid").that.is.a("string");
        expect(auth).to.have.property("online", true);
        expect(auth).to.have.property("created_at").that.is.a("number");
        token = auth.token;
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
        email: "user@example.com",
        pubkey: "the-pubkey",
        meta: '{"pass":"secret2"}',
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


});
