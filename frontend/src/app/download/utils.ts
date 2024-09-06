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

const save_track = (dir: string) => {
  return api
    .post({ dir: dir }, "/api/youtubedl/save_track/")
    .res(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = dir.split("/").pop() || "downloaded_file";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    })
    .catch(error => {
      console.error("File download failed:", error);
    });
};

/**
 * Exports YoutubeDL related actions.
 * @returns {Object} An object containing all the YoutubeDL actions.
 */
export const YoutubeDLActions = () => {
  return {
    download,
    save_track,
  };
};
