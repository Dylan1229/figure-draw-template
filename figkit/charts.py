"""Chart builders: one function per figure shape we actually publish.

Each returns the matplotlib artists so you can keep customising -- these are
thin, opinionated wrappers, not a walled garden. If a helper is 80% right,
call it and then talk to the returned axes/bars directly.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .annotate import bar_labels
from .palette import DEFAULT_COLORS, RICE, text_on
from .style import REL, bold_ticks, grid, rel_fontsize

_EDGE = dict(edgecolor="black", lw=0.8)


# --------------------------------------------------------------------------
# bars
# --------------------------------------------------------------------------

def grouped_bar(ax, categories: Sequence[str], series: Sequence[Sequence[float]],
                labels: Sequence[str] | None = None,
                colors: Sequence[str] | None = None, *,
                total_width: float = 0.72, ylabel: str | None = None,
                annotate: str | None = "outside", fmt: str = "{:g}",
                alpha: float = 0.95, edge: bool = True,
                label_fontsize: int | None = None) -> tuple[np.ndarray, list]:
    """Vertical grouped bars -- the default "compare N systems over M settings".

    Args:
        categories: X groups (e.g. `["2K", "4K"]`).
        series: One sequence per system, each as long as `categories`.
        annotate: `"outside"`, `"inside"`, `"mid"`, or None.

    Returns:
        `(x_centers, [BarContainer, ...])`.
    """
    data = np.asarray(series, dtype=float)
    if data.ndim != 2:
        raise ValueError("`series` must be 2D: one row per legend entry")
    n_series, n_cats = data.shape
    if n_cats != len(categories):
        raise ValueError(f"{n_cats} values per series but {len(categories)} categories")

    colors = list(colors or DEFAULT_COLORS)
    width = total_width / n_series
    x = np.arange(n_cats, dtype=float)
    containers = []
    for i in range(n_series):
        offset = (i - (n_series - 1) / 2) * width
        bars = ax.bar(x + offset, data[i], width,
                      label=labels[i] if labels else None,
                      color=colors[i % len(colors)], alpha=alpha,
                      **(_EDGE if edge else {}))
        containers.append(bars)
        if annotate:
            bar_labels(ax, bars, fmt=fmt, where=annotate, fontsize=label_fontsize)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontweight="bold")
    grid(ax, axis="y")
    bold_ticks(ax)
    return x, containers


def hbar(ax, labels: Sequence[str], values: Sequence[float],
         color: str | Sequence[str] = RICE["ours"], *,
         height: float = 0.62, xlabel: str | None = None,
         annotate: str | None = "inside", fmt: str = "{:g}",
         order: str = "top_down", alpha: float = 0.95, edge: bool = True,
         label_fontsize: int | None = None):
    """Horizontal bars, first label at the top.

    Prefer this over vertical bars when category names are long (`"+ Region-aware
    Cache Control"` will never fit under a vertical bar) or when there are more
    than ~5 categories.

    Args:
        order: `"top_down"` keeps `labels[0]` at the top (what readers expect
            for a ranked list); `"bottom_up"` is matplotlib's raw order.

    Returns:
        `(y_positions, BarContainer)`.
    """
    n = len(values)
    y = np.arange(n, dtype=float)[::-1] if order == "top_down" else np.arange(n, dtype=float)
    colors = [color] * n if isinstance(color, str) else list(color)
    bars = ax.barh(y, list(values), height, color=colors, alpha=alpha,
                   **(_EDGE if edge else {}))
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontweight="bold")
    if annotate:
        bar_labels(ax, bars, fmt=fmt, where=annotate, horizontal=True,
                   fontsize=label_fontsize)
    grid(ax, axis="x")
    bold_ticks(ax)
    return y, bars


def paired_bar(ax, groups: Sequence[str], before: Sequence[float],
               after: Sequence[float], *, labels: tuple[str, str] = ("w/o", "w/"),
               colors: tuple[str, str] = (RICE["other_baseline"], RICE["ours"]),
               width: float = 0.36, ylabel: str | None = None,
               annotate: str | None = "mid", fmt: str = "{:g}",
               label_fontsize: int | None = None):
    """Two bars per group: the "with vs. without" ablation shape.

    Pair this with `annotate.speedup(..., style="bracket")` to label the delta
    on every group.

    Returns:
        `(x_centers, bars_before, bars_after)`.
    """
    x = np.arange(len(groups), dtype=float)
    b0 = ax.bar(x - width / 2, list(before), width, color=colors[0],
                label=labels[0], alpha=0.95, **_EDGE)
    b1 = ax.bar(x + width / 2, list(after), width, color=colors[1],
                label=labels[1], alpha=0.95, **_EDGE)
    if annotate:
        for bars in (b0, b1):
            bar_labels(ax, bars, fmt=fmt, where=annotate, fontsize=label_fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontweight="bold")
    grid(ax, axis="y")
    bold_ticks(ax)
    return x, b0, b1


def stacked_hbar(ax, labels: Sequence[str], matrix: Sequence[Sequence[float]],
                 parts: Sequence[str], colors: Sequence[str] | None = None, *,
                 xlabel: str | None = None, show_pct: bool = True,
                 min_pct: float = 6.0, show_totals: bool = True,
                 total_fmt: str = "{:.0f} s", order: str = "top_down",
                 height: float = 0.6, label_fontsize: int | None = None):
    """Composition breakdown: where does the time go?

    Args:
        matrix: `len(labels)` rows x `len(parts)` columns of absolute values.
        show_pct: Label each segment with its share. Absolute totals go at the
            end of the bar -- percentages inside, magnitude outside, so the
            figure answers both "what dominates" and "how big is it".
        min_pct: Segments smaller than this are left unlabelled rather than
            rendered as unreadable overlapping text.

    Returns:
        `(y_positions, [BarContainer, ...])`.
    """
    data = np.asarray(matrix, dtype=float)
    totals = data.sum(axis=1)
    pct = (data.T / totals * 100).T
    n = len(labels)
    if order == "top_down":
        data, pct, totals = data[::-1], pct[::-1], totals[::-1]
        labels = list(labels)[::-1]
    y = np.arange(n, dtype=float)
    colors = list(colors or DEFAULT_COLORS)
    fs = label_fontsize or rel_fontsize(REL["value"])

    left = np.zeros(n)
    containers = []
    for j, part in enumerate(parts):
        col = colors[j % len(colors)]
        bars = ax.barh(y, data[:, j], left=left, height=height, label=part,
                       color=col, edgecolor="white", lw=1.0)
        containers.append(bars)
        if show_pct:
            for i in range(n):
                if pct[i, j] >= min_pct:
                    ax.text(left[i] + data[i, j] / 2, y[i], f"{pct[i, j]:.0f}%",
                            ha="center", va="center", color=text_on(col),
                            fontsize=fs, fontweight="bold")
        left += data[:, j]

    if show_totals:
        pad = totals.max() * 0.015
        for i in range(n):
            ax.text(totals[i] + pad, y[i], total_fmt.format(totals[i]),
                    va="center", ha="left", fontsize=fs + 1,
                    fontweight="bold", color="#333333")
        ax.set_xlim(0, totals.max() * 1.16)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontweight="bold")
    grid(ax, axis="x")
    bold_ticks(ax)
    return y, containers


# --------------------------------------------------------------------------
# lines
# --------------------------------------------------------------------------

def scaling_lines(ax, series: Mapping[str, Mapping[float, float] | tuple],
                  colors: Sequence[str] | None = None, *,
                  markers: Sequence[str] = ("o", "s", "^", "D", "v"),
                  linestyles: Sequence[str] = ("-", "--", "-.", ":"),
                  xlabel: str | None = None, ylabel: str | None = None,
                  annotate_ratio: bool = True, annotate_first: bool = False,
                  fmt: str = "{:.1f}x",
                  lw: float = 2.6, markersize: float = 8,
                  xticks: Sequence[float] | None = None,
                  label_fontsize: int | None = None):
    """Latency/throughput vs. a scaling knob (GPUs, batch size, resolution).

    Args:
        series: `{name: {x: y}}` or `{name: (xs, ys)}`. Series may have
            different x support -- an 8-GPU point that only exists for 4K is
            fine.
        annotate_ratio: Label each point with its speedup over that series'
            first point. This is what turns a line plot into a scaling claim;
            the reader no longer has to divide numbers in their head.
        annotate_first: Also label the reference point with "1.0x". Off by
            default -- it is noise, and the reader can see it is the baseline.

    Returns:
        `{name: Line2D}`.
    """
    colors = list(colors or DEFAULT_COLORS)
    fs = label_fontsize or rel_fontsize(REL["value"] * 0.92)
    lines = {}
    all_x: set[float] = set()
    for i, (name, raw) in enumerate(series.items()):
        if isinstance(raw, Mapping):
            xs = sorted(raw)
            ys = [raw[x] for x in xs]
        else:
            xs, ys = list(raw[0]), list(raw[1])
        all_x.update(xs)
        color = colors[i % len(colors)]
        (line,) = ax.plot(xs, ys, color=color, marker=markers[i % len(markers)],
                          ls=linestyles[i % len(linestyles)], lw=lw,
                          markersize=markersize, label=name)
        lines[name] = line
        if annotate_ratio:
            base = ys[0]
            for x, y in list(zip(xs, ys))[0 if annotate_first else 1:]:
                ax.annotate(fmt.format(base / y), (x, y), xytext=(4, 8),
                            textcoords="offset points", fontsize=fs,
                            fontweight="bold", color=color)
    if xlabel:
        ax.set_xlabel(xlabel, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontweight="bold")
    ax.set_xticks(sorted(all_x) if xticks is None else list(xticks))
    grid(ax, axis="both")
    bold_ticks(ax)
    return lines


# --------------------------------------------------------------------------
# matrices
# --------------------------------------------------------------------------

def heatmap(ax, matrix: Sequence[Sequence[float]],
            xticklabels: Sequence, yticklabels: Sequence, *,
            cmap="viridis", fmt: str = "{:.1f}", annotate: bool = True,
            cbar: bool = True, cbar_label: str | None = None,
            xlabel: str | None = None, ylabel: str | None = None,
            title: str | None = None, vmin: float | None = None,
            vmax: float | None = None, label_fontsize: int | None = None):
    """Two-parameter sweep. Rows = y parameter, columns = x parameter.

    Always annotate the cells for a small grid (<= ~8x8): color communicates the
    trend, the number lets a reader quote your result. Use
    `palette.sequential_cmap(color)` so the heatmap stays inside the paper's
    color language.

    Returns:
        The `AxesImage`.
    """
    data = np.asarray(matrix, dtype=float)
    im = ax.imshow(data, cmap=cmap, aspect="auto", interpolation="nearest",
                   vmin=vmin, vmax=vmax)
    ax.set_xticks(range(data.shape[1]))
    ax.set_xticklabels(xticklabels, fontweight="bold")
    ax.set_yticks(range(data.shape[0]))
    ax.set_yticklabels(yticklabels, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, fontweight="bold")
    if title:
        ax.set_title(title, fontweight="bold")
    if annotate:
        # Per-cell text color from the *rendered* cell color, not from a
        # midpoint guess: a mid-tone cell in a light colormap keeps dark text.
        fs = label_fontsize or rel_fontsize(REL["cell"])
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                v = data[i, j]
                ax.text(j, i, fmt.format(v), ha="center", va="center",
                        color=text_on(im.cmap(im.norm(v))),
                        fontsize=fs, fontweight="bold")
    if cbar:
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if cbar_label:
            cb.set_label(cbar_label, fontweight="bold")
    ax.grid(False)
    return im


# --------------------------------------------------------------------------
# two quantities, one axis
# --------------------------------------------------------------------------

def mirror_bars(ax, positions: Sequence[float],
                up_values: Sequence[float], down_values: Sequence[float], *,
                up_range: tuple[float, float], down_range: tuple[float, float],
                up_label: str = "Quality", down_label: str = "Latency (s)",
                up_color: str = RICE["highlight"], down_color: str = RICE["ours"],
                up_fmt: str = "{:.1f}", down_fmt: str = "{:.0f}",
                up_nticks: int = 6, down_nticks: int = 6,
                label_x: float = -0.14, bottom_pad: float = 1.24,
                width: float = 0.8, label_fontsize: int | None = None):
    """Quality up, cost down, sharing one x axis: the trade-off figure.

    Two metrics with incompatible units are each mapped onto their own half of
    the axis, so "quality falls off a cliff after 8 tiles while latency barely
    improves" is one glance instead of two figures the reader must align.

    Args:
        up_range / down_range: `(min, max)` of the real values for each half.
            Choose them deliberately -- they set what "a big difference" looks
            like, and a too-wide range flattens your effect. Pick round
            endpoints so the tick labels come out round.
        up_nticks / down_nticks: Tick counts per half. Set them so
            `linspace(min, max, n)` lands on round numbers.
        bottom_pad: Extra room under the downward bars, as a multiple of the
            upward span -- somewhere to put group labels.

    Returns:
        `(up_bars, down_bars)`.
    """
    up = np.asarray(up_values, dtype=float)
    down = np.asarray(down_values, dtype=float)
    (u_min, u_max), (d_min, d_max) = up_range, down_range
    u_span, d_span = u_max - u_min, d_max - d_min
    scale = u_span / d_span
    fs = label_fontsize or rel_fontsize(REL["value"])

    bu = ax.bar(positions, up - u_min, width, color=up_color, alpha=0.9,
                label=up_label, **_EDGE)
    bd = ax.bar(positions, -(down - d_min) * scale, width, color=down_color,
                alpha=0.9, label=down_label, **_EDGE)
    for bar, v in zip(bu, up):
        ax.annotate(up_fmt.format(v), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center",
                    va="bottom", fontsize=fs, fontweight="bold")
    for bar, v in zip(bd, down):
        ax.annotate(down_fmt.format(v), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, -4), textcoords="offset points", ha="center",
                    va="top", fontsize=fs, fontweight="bold")

    ax.axhline(0, color="black", lw=1.8, alpha=0.85)
    ax.set_yticks(list(np.linspace(0, u_span, up_nticks)) +
                  list(np.linspace(0, -u_span, down_nticks)))
    ax.set_yticklabels([f"{v:g}" for v in np.linspace(u_min, u_max, up_nticks)] +
                       [f"{v:g}" for v in np.linspace(d_min, d_max, down_nticks)])
    ax.set_ylim(-u_span * bottom_pad, u_span * 1.05)
    ax.text(label_x, u_span / 2, up_label, transform=ax.get_yaxis_transform(),
            rotation=90, ha="center", va="center", fontweight="bold",
            fontsize=fs)
    ax.text(label_x, -u_span / 2, down_label, transform=ax.get_yaxis_transform(),
            rotation=90, ha="center", va="center", fontweight="bold",
            fontsize=fs)
    grid(ax, axis="y")
    bold_ticks(ax)
    return bu, bd


def side_table(ax, rows: Sequence[Sequence[str]], col_labels: Sequence[str], *,
               title: str | None = None, header_rows: Sequence[int] = (),
               col_widths: Sequence[float] | None = None,
               fontsize: int | None = None, scale_y: float = 1.25):
    """A small table pinned beside a panel, drawn on its own (blank) axis.

    For the configuration detail that belongs *with* the figure but would bloat
    the caption ("what tile size is `#tiles=12`?"). Give it a narrow column in
    `gridspec_kw={"width_ratios": [4, 1.2]}`.

    Args:
        header_rows: Indices into `rows` to shade as section headers.

    Returns:
        The matplotlib `Table`.
    """
    fontsize = fontsize or rel_fontsize(REL["table"])
    ax.axis("off")
    table = ax.table(cellText=[list(r) for r in rows], colLabels=list(col_labels),
                     cellLoc="center", loc="center",
                     colWidths=list(col_widths) if col_widths else None)
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1.0, scale_y)
    n_cols = len(col_labels)
    for r in range(len(rows) + 1):
        for c in range(n_cols):
            cell = table[(r, c)]
            cell.set_edgecolor("black")
            cell.set_linewidth(0.6)
    for c in range(n_cols):
        table[(0, c)].set_facecolor("#F0F0F0")
        table[(0, c)].get_text().set_fontweight("bold")
    for r in header_rows:
        for c in range(n_cols):
            table[(r + 1, c)].set_facecolor("#E6E6E6")
            table[(r + 1, c)].get_text().set_fontweight("bold")
    if title:
        ax.text(0.5, 0.87, title, ha="center", va="bottom", fontweight="bold",
                fontsize=fontsize + 1, transform=ax.transAxes)
    return table
