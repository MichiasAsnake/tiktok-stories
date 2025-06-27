import fetchWrapper from "./fetch-wrapper.js";
import storyCard from "./utils.js";
const stories = new fetchWrapper();

console.log(
  stories.get("mock-stories.json").then((data) => {
    console.log(
      data.stories.forEach((story) => {
        document
          .querySelector(".stories")
          .insertAdjacentHTML("beforeend", new storyCard(story).render());
      })
    );
  })
);
