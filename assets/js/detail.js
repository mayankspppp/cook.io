/**
 * @license MIT
 * @copyright 2023 codewithsadee
 * @author codewithsadee <mohammadsadee24@gmail.com>
 */

"use strict";

import { fetchData } from "./api.js";
import { getTime } from "./module.js";

const $detailContainer = document.querySelector("[data-detail-container]");
const recipeId = new URLSearchParams(window.location.search).get("recipe");

window.showFetchError = (message) => {
  $detailContainer.innerHTML = `
    <div class="detail-error">
      <h1 class="headline-small">Recipe unavailable</h1>
      <p class="body-large">${message || "We could not load this recipe."}</p>
      <a href="./recipes.html" class="btn btn-primary">Browse recipes</a>
    </div>
  `;
};

if (!recipeId) {
  window.showFetchError("No recipe was specified.");
} else {
  window.ACCESS_POINT = `https://api.edamam.com/api/recipes/v2/${encodeURIComponent(recipeId)}`;

  fetchData(null, (data) => {
    if (!data?.recipe) {
      window.showFetchError("We could not find that recipe.");
      return;
    }

    const {
      images: { LARGE, REGULAR, SMALL, THUMBNAIL },
      label: title,
      source: author,
      ingredients = [],
      totalTime: cookingTime = 0,
      calories = 0,
      cuisineType = [],
      dietLabels = [],
      dishType = [],
      yield: servings = 0,
      ingredientLines = [],
      uri,
    } = data.recipe;

    document.title = `${title} - cook.io`;

    const banner = LARGE ?? REGULAR ?? SMALL ?? THUMBNAIL;
    const bannerUrl = banner?.url || "";
    const tags = [...cuisineType, ...dietLabels, ...dishType];
    let tagElements = "";
    let ingredientItems = "";

    const currentRecipeId =
      uri?.slice(uri.lastIndexOf("_") + 1) || recipeId;
    const isSaved = window.localStorage.getItem(
      `cookio-recipe${currentRecipeId}`
    );

    tags.forEach((tag) => {
      let type = "";
      if (cuisineType.includes(tag)) {
        type = "cuisineType";
      } else if (dietLabels.includes(tag)) {
        type = "diet";
      } else {
        type = "dishType";
      }

      tagElements += `<a href="./recipes.html?${type}=${encodeURIComponent(
        tag.toLowerCase()
      )}" class="filter-chip label-large has-state">${tag}</a>`;
    });

    ingredientLines.forEach((ingredient) => {
      ingredientItems += `<li class="ignr-item">${ingredient}</li>`;
    });

    $detailContainer.innerHTML = `
      <figure class="detail-banner img-holder">
        ${
          bannerUrl
            ? `<img src="${bannerUrl}" width="${banner.width || 400}" height="${
                banner.height || 400
              }" alt="${title}" loading="lazy" class="img-cover" />`
            : ""
        }
      </figure>

      <div class="detail-content">
        <div class="title-wrapper">
          <h1 class="display-small">${title ?? "Untitled"}</h1>
          <button class="btn btn-secondary has-state has-icon ${
            isSaved ? "saved" : "removed"
          }" onclick="saveRecipe(this,'${currentRecipeId}')">
            <span class="material-symbols-outlined bookmark-add" aria-hidden="true">bookmark_add</span>
            <span class="material-symbols-outlined bookmark" aria-hidden="true">bookmark</span>
            <span class="label-large save-text">Save</span>
            <span class="label-large unsaved-text">Unsaved</span>
          </button>
        </div>

        <div class="details-author label-large">
          <span class="span">by</span> ${author || "Unknown"}
        </div>

        <div class="detail-stats">
          <div class="stats-item">
            <span class="display-medium">${ingredients.length}</span>
            <span class="label-medium">Ingredients</span>
          </div>
          <div class="stats-item">
            <span class="display-medium">${getTime(cookingTime).time || "<1"}</span>
            <span class="label-medium">${getTime(cookingTime).timeUnit || "Minute"}</span>
          </div>
          <div class="stats-item">
            <span class="display-medium">${Math.floor(calories)}</span>
            <span class="label-medium">Calories</span>
          </div>
        </div>

        ${
          tagElements
            ? `<div class="tag-list">${tagElements}</div>`
            : ""
        }

        <h2 class="title-medium ingr-title">
          Ingredients <span class="label-small">for ${servings} Servings</span>
        </h2>

        ${
          ingredientItems
            ? `<ul class="body-large ignr-list">${ingredientItems}</ul>`
            : ""
        }
      </div>
    `;
  });
}
