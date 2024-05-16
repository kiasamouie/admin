import wretch from "wretch";
import Cookies from "js-cookie";

// Base API setup for making HTTP requests
const api = wretch("http://localhost:8000").accept("application/json");

/**
 * Download using YoutubeDL with url.
 * @param {string} url - The YoutubeDL url.
 * @returns {Promise} A promise that resolves with the download response.
 */
const download = (url: string) => {
  return api.post({ url: url }, "/api/youtubedl/download/");
};

/**
 * Exports YoutubeDL related actions.
 * @returns {Object} An object containing all the YoutubeDL actions.
 */
export const YoutubeDLActions = () => {
  return {
    download,
  };
};
