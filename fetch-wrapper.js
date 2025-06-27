export default class fetchWrapper {
  get(url) {
    return fetch(url).then((response) => response.json());
  }
  post(url, data) {
    return fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
    }).then((response) => response.json());
  }
}
