// On the Tags page, open the tag linked to from a page's tags (e.g. #tag:mcf)
function openLinkedTag() {
  if (!location.hash.startsWith("#tag:")) return;
  const heading = document.getElementById(decodeURIComponent(location.hash.slice(1)));
  const listing = heading && heading.closest("details.tag-listing");
  if (listing) listing.open = true;
}

// `document$` fires on every page load, including instant navigation
if (typeof document$ !== "undefined") {
  document$.subscribe(openLinkedTag);
} else {
  document.addEventListener("DOMContentLoaded", openLinkedTag);
}
window.addEventListener("hashchange", openLinkedTag);
