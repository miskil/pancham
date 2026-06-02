import { useEffect, useMemo, useState } from "react";

function avatarSeed(name = "") {
  const text = String(name || "").trim();
  if (!text) return "A";
  return text.charAt(0).toUpperCase();
}

function formatWhen(value) {
  const dt = value ? new Date(value) : null;
  if (!dt || Number.isNaN(dt.getTime())) return "Just now";
  return dt.toLocaleString("en-IN", { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" });
}

function excerpt(text, maxChars = 150) {
  const clean = String(text || "").trim();
  if (clean.length <= maxChars) return { text: clean, truncated: false };
  return { text: `${clean.slice(0, maxChars).trimEnd()}...`, truncated: true };
}

function roleLabel(post) {
  return post.author_role === "ADMIN" ? "Official Update" : "Community Project";
}

export function AnubhavFeed({ api }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("ALL");
  const [expanded, setExpanded] = useState({});

  const [form, setForm] = useState({ title: "", body: "" });
  const [submitting, setSubmitting] = useState(false);
  const [photo, setPhoto] = useState(null);
  const [photoError, setPhotoError] = useState(null);

  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({ title: "", body: "" });

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listAnubhavPosts();
      setPosts(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load posts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!form.title.trim() || !form.body.trim()) return;
    setSubmitting(true);
    setPhotoError(null);
    try {
      const created = await api.createAnubhavPost({ title: form.title.trim(), body: form.body.trim() });
      if (photo && created?.id && typeof api.uploadAnubhavMedia === "function") {
        const formData = new FormData();
        formData.append("file", photo);
        await api.uploadAnubhavMedia(created.id, formData);
      }
      setForm({ title: "", body: "" });
      setPhoto(null);
      await load();
    } catch (err) {
      const message = err.message || "Failed to create post";
      setPhotoError(message);
      alert(message);
    } finally {
      setSubmitting(false);
    }
  }

  function handlePhotoChange(e) {
    const selected = e.target.files?.[0] || null;
    if (!selected) {
      setPhoto(null);
      setPhotoError(null);
      return;
    }
    if (!selected.type || !selected.type.startsWith("image/")) {
      setPhotoError("Please select an image file only");
      setPhoto(null);
      return;
    }
    setPhoto(selected);
    setPhotoError(null);
  }

  async function handleUpdate(post) {
    if (!editForm.title.trim() || !editForm.body.trim()) return;
    try {
      await api.updateAnubhavPost(post.id, { title: editForm.title.trim(), body: editForm.body.trim() });
      setEditingId(null);
      await load();
    } catch (err) {
      alert(err.message || "Failed to update post");
    }
  }

  async function handleDelete(post) {
    if (!confirm("Delete this post?")) return;
    try {
      await api.deleteAnubhavPost(post.id);
      await load();
    } catch (err) {
      alert(err.message || "Failed to delete post");
    }
  }

  function startEdit(post) {
    setEditingId(post.id);
    setEditForm({ title: post.title, body: post.body });
  }

  const filteredPosts = useMemo(() => {
    if (filter === "VILLAGE") return posts.filter((p) => p.author_role === "VILLAGE");
    if (filter === "ADMIN") return posts.filter((p) => p.author_role === "ADMIN");
    return posts;
  }, [posts, filter]);

  return (
    <div className="anubhav-page">
      <header className="anubhav-header">
        <h2 className="anubhav-title">Anubhav</h2>
        <p className="anubhav-subtitle">Stories of progress and resilience from the heart of our communities.</p>
      </header>

      <section className="anubhav-composer">
        <div className="anubhav-composer-head">
          <div className="anubhav-avatar">A</div>
          <div className="anubhav-composer-copy">
            <p className="anubhav-composer-prompt">What's happening in your village?</p>
            <p className="anubhav-composer-note">Share one clear story with title and details.</p>
          </div>
        </div>

        <form onSubmit={handleCreate} className="anubhav-form">
          <input
            type="text"
            placeholder="Story title"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            className="anubhav-input"
            required
          />
          <textarea
            placeholder="Write your story..."
            value={form.body}
            onChange={(e) => setForm((f) => ({ ...f, body: e.target.value }))}
            rows={4}
            className="anubhav-input anubhav-textarea"
            required
          />
          <div className="anubhav-form-actions">
            <label className="anubhav-photo-btn">
              Add Photo
              <input type="file" accept="image/*" className="hidden" onChange={handlePhotoChange} />
            </label>
            {photo && <span className="anubhav-photo-name">{photo.name}</span>}
            <button type="submit" disabled={submitting} className="anubhav-post-btn">
              {submitting ? "Posting..." : "Post Story"}
            </button>
          </div>
          {photoError && <p className="text-xs text-red-600">{photoError}</p>}
        </form>
      </section>

      <div className="anubhav-filters" role="tablist" aria-label="Anubhav filters">
        <button className={`anubhav-chip ${filter === "ALL" ? "is-active" : ""}`} onClick={() => setFilter("ALL")}>All Stories</button>
        <button className={`anubhav-chip ${filter === "VILLAGE" ? "is-active" : ""}`} onClick={() => setFilter("VILLAGE")}>Villages</button>
        <button className={`anubhav-chip ${filter === "ADMIN" ? "is-active" : ""}`} onClick={() => setFilter("ADMIN")}>Admin Updates</button>
      </div>

      {loading && <div className="text-sm text-ink-400">Loading stories...</div>}
      {error && <div className="text-sm text-red-600">{error}</div>}

      {!loading && filteredPosts.length === 0 && (
        <div className="anubhav-empty">No stories yet. Be the first to share.</div>
      )}

      <section className="anubhav-feed">
        {filteredPosts.map((post) => {
          const expandedNow = Boolean(expanded[post.id]);
          const shortBody = excerpt(post.body, 190);
          const displayBody = expandedNow || !shortBody.truncated ? post.body : shortBody.text;
          return (
            <article key={post.id} className="anubhav-card">
              {editingId === post.id ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))}
                    className="anubhav-input"
                  />
                  <textarea
                    value={editForm.body}
                    onChange={(e) => setEditForm((f) => ({ ...f, body: e.target.value }))}
                    rows={5}
                    className="anubhav-input anubhav-textarea"
                  />
                  <div className="flex gap-2">
                    <button onClick={() => handleUpdate(post)} className="anubhav-post-btn">Save Story</button>
                    <button onClick={() => setEditingId(null)} className="anubhav-ghost-btn">Cancel</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="anubhav-card-head">
                    <div className="anubhav-author-wrap">
                      <div className="anubhav-avatar tone-village">{avatarSeed(post.author_display_name)}</div>
                      <div>
                        <p className="anubhav-author">{post.author_display_name}</p>
                        <p className="anubhav-meta">{formatWhen(post.created_at)} • {roleLabel(post)}</p>
                      </div>
                    </div>
                    {post.can_edit && (
                      <div className="anubhav-card-actions">
                        <button onClick={() => startEdit(post)} className="anubhav-link-btn">Edit</button>
                        <button onClick={() => handleDelete(post)} className="anubhav-link-btn danger">Delete</button>
                      </div>
                    )}
                  </div>

                  <h3 className="anubhav-story-title">{post.title}</h3>
                  <p className="anubhav-story-body">{displayBody}</p>

                  {shortBody.truncated && (
                    <button
                      onClick={() => setExpanded((s) => ({ ...s, [post.id]: !s[post.id] }))}
                      className="anubhav-readmore"
                    >
                      {expandedNow ? "Show less" : "Read More"}
                    </button>
                  )}

                  {Array.isArray(post.media_files) && post.media_files.length > 0 ? (
                    <div className="anubhav-media-grid">
                      {post.media_files.map((media) => (
                        <img
                          key={media.id}
                          src={media.file_url}
                          alt={`${post.title} media`}
                          className="anubhav-media-item"
                          loading="lazy"
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="anubhav-story-visual" aria-hidden="true">
                      <span className="anubhav-visual-badge">{post.author_display_name}</span>
                    </div>
                  )}
                </>
              )}
            </article>
          );
        })}
      </section>
    </div>
  );
}
