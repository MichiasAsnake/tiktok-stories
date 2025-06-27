class storyCard {
  constructor(story) {
    this.story = story;
  }

  render() {
    return ` 
    <div class="story-card">
    <img class="story-image" src="${this.story.imageUrl}" alt="${
      this.story.title
    }" />   
    <div class="story-card-header">
    <div class="story-card-content">
    <h2>${this.story.title}</h2>
    <p>${this.story.summary}</p>
    </div>
    <div class="key-points">
      ${this.story.keyPoints
        .map((point) => `<p class="key-point">${point}</p>`)
        .join("")}
        </div>
        <div class="card-stats">
    <p>Video Count: ${this.story.videoCount}</p>
    <p>Comment Count: ${this.story.commentCount}</p>
    <p>Sentiment: ${this.story.sentiment}</p>
    </div>
    </div>
    </div>`;
  }
}
export default storyCard;
