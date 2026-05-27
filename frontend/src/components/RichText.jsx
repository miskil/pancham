import { useEffect, useRef } from "react";

const URL_RE = /https?:\/\/[^\s]+/g;
const IG_RE = /https?:\/\/(?:www\.)?instagram\.com\/p\/([^/?#\s]+)/;

function InstagramEmbed({ url }) {
  const ref = useRef(null);

  useEffect(() => {
    if (window.instgrm) {
      window.instgrm.Embeds.process();
    } else if (!document.getElementById("ig-embed-script")) {
      const s = document.createElement("script");
      s.id = "ig-embed-script";
      s.src = "https://www.instagram.com/embed.js";
      s.async = true;
      document.body.appendChild(s);
    }
  }, [url]);

  return (
    <div ref={ref} className="my-2">
      <blockquote
        className="instagram-media"
        data-instgrm-permalink={url}
        data-instgrm-version="14"
        data-instgrm-captioned
        style={{ maxWidth: "100%", minWidth: 0, width: "100%" }}
      />
    </div>
  );
}

export function RichText({ text, className = "" }) {
  if (!text) return null;

  const igUrls = [];
  const parts = [];
  let last = 0;

  for (const match of text.matchAll(URL_RE)) {
    const url = match[0].replace(/[.,;!?)]+$/, ""); // strip trailing punctuation
    const start = match.index;
    const end = start + url.length;

    if (start > last) parts.push(<span key={last}>{text.slice(last, start)}</span>);

    if (IG_RE.test(url)) {
      igUrls.push(url);
      parts.push(
        <a key={start} href={url} target="_blank" rel="noopener noreferrer"
          className="text-primary-600 underline break-all">
          {url}
        </a>
      );
    } else {
      parts.push(
        <a key={start} href={url} target="_blank" rel="noopener noreferrer"
          className="text-primary-600 underline break-all">
          {url}
        </a>
      );
    }
    last = end;
  }
  if (last < text.length) parts.push(<span key={last}>{text.slice(last)}</span>);

  return (
    <div>
      <p className={`text-sm text-gray-700 whitespace-pre-wrap ${className}`}>{parts}</p>
      {igUrls.map((u) => <InstagramEmbed key={u} url={u} />)}
    </div>
  );
}
