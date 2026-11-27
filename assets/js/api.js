/**
 * Legacy browser-side Edamam access has been retired. Recipe data is now
 * bundled locally and served by the Streamlit application.
 */

"use strict";

export const fetchData = async function () {
  throw new Error(
    "The legacy recipe client is retired. Run `streamlit run app.py` to use Cook.io."
  );
};
