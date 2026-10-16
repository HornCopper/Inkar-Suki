"""Validated announcement diff payloads and escaped, local-only HTML rendering."""

from difflib import SequenceMatcher
from html import escape
from itertools import zip_longest
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AnnouncementSectionDiff(BaseModel):
    path: list[str] = Field(min_length=1)
    before: list[str] = Field(default_factory=list)
    after: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_change(self):
        if self.before == self.after:
            raise ValueError("章节必须包含正文差异")
        return self


class BetaAnnouncementDiff(BaseModel):
    schema_version: Literal[1] = 1
    title: str = "剑网3体服更新"
    update_time: str = ""
    client_version: str = ""
    previous_recorded_at: str = ""
    recorded_at: str = ""
    sections: list[AnnouncementSectionDiff] = Field(min_length=1)


def _inline_diff(before: str, after: str) -> tuple[str, str]:
    old_parts, new_parts = [], []
    for tag, i, j, k, l in SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag == "equal":
            old_parts.append(escape(before[i:j]))
            new_parts.append(escape(after[k:l]))
        else:
            if tag in {"delete", "replace"}:
                old_parts.append(f'<del>{escape(before[i:j])}</del>')
            if tag in {"insert", "replace"}:
                new_parts.append(f'<mark>{escape(after[k:l])}</mark>')
    return "".join(old_parts), "".join(new_parts)


def _cell(text: str | None, kind: str = "context", *, markup: bool = False) -> str:
    if text is None:
        return '<div class="diff-cell absent">—</div>'
    content = escape(text)
    if markup:
        content = text
    elif kind == "added":
        content = f"<mark>{content}</mark>"
    elif kind == "removed":
        content = f"<del>{content}</del>"
    return f'<div class="diff-cell {kind}">{content}</div>'


def _row(old: str, new: str) -> str:
    return f'<div class="diff-row">{old}{new}</div>'


def _section_body(section: AnnouncementSectionDiff) -> str:
    parts = []
    for tag, i, j, k, l in SequenceMatcher(
        None, section.before, section.after, autojunk=False,
    ).get_opcodes():
        if tag == "equal":
            parts.extend(_row(_cell(line), _cell(line)) for line in section.after[k:l])
        elif tag == "delete":
            parts.extend(_row(_cell(line, "removed"), _cell(None)) for line in section.before[i:j])
        elif tag == "insert":
            parts.extend(_row(_cell(None), _cell(line, "added")) for line in section.after[k:l])
        else:
            for old, new in zip_longest(section.before[i:j], section.after[k:l]):
                if old is None:
                    parts.append(_row(_cell(None), _cell(new, "added")))
                elif new is None:
                    parts.append(_row(_cell(old, "removed"), _cell(None)))
                elif SequenceMatcher(None, old, new, autojunk=False).ratio() < 0.4:
                    parts.append(_row(_cell(old, "removed"), _cell(new, "added")))
                else:
                    old_html, new_html = _inline_diff(old, new)
                    parts.append(_row(
                        _cell(old_html, "modified", markup=True),
                        _cell(new_html, "modified", markup=True),
                    ))
    return "".join(parts)


def build_beta_diff_html(
    diff: BetaAnnouncementDiff, font_uri: str, *,
    bot_name: str = "Inkar-Suki", footer_message: str = "",
) -> str:
    sections = []
    for section in diff.sections:
        kind = "新增章节" if not section.before else "删除章节" if not section.after else "章节修改"
        path = " / ".join(escape(part) for part in section.path)
        sections.append(
            f'<section><h2>{path}<span class="section-kind">{kind}</span></h2>'
            '<div class="diff-row column-headings"><div>更新前</div><div>更新后</div></div>'
            f'{_section_body(section)}</section>'
        )
    compared = ""
    if diff.previous_recorded_at:
        compared = f'<p class="comparison">对比基线：{escape(diff.previous_recorded_at)}</p>'
    footer_text = escape(f"{bot_name}: {footer_message}" if footer_message else bot_name)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Harmony; src: url('{escape(font_uri, quote=True)}'); }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #fff; font-family: Harmony, sans-serif; color: #2c3e50; }}
.beta-diff {{ width: 1600px; padding: 32px; background: #fff; }}
.diff-heading {{ border-bottom: 2px solid #dce4eb; padding-bottom: 20px; }}
h1 {{ font-size: 30px; margin: 0 0 10px; }}
.metadata, .comparison {{ margin: 6px 0; color: #667788; font-size: 17px; }}
.legend {{ margin-top: 16px; font-size: 18px; }}
.legend span {{ margin-right: 18px; }}
section {{ margin-top: 26px; }}
h2 {{ margin: 0 0 12px; font-size: 22px; line-height: 1.6; overflow-wrap: anywhere; }}
.section-kind {{ display: inline-block; margin-left: 12px; font-size: 15px; color: #718096; }}
.diff-row {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 20px; }}
.column-headings {{ margin-bottom: 8px; font-size: 18px; font-weight: bold; color: #536477; }}
.column-headings > div {{ padding: 10px 14px; background: #f1f4f7; }}
.diff-cell {{ margin: 4px 0; padding: 8px 12px; font-size: 22px; line-height: 1.8;
    white-space: pre-wrap; overflow-wrap: anywhere; border-left: 3px solid transparent; }}
.context {{ color: #677482; }}
.absent {{ color: #b4bec8; background: #f8f9fa; text-align: center; }}
.added {{ border-color: #219667; background: #f0faf5; }}
.removed {{ border-color: #d05252; background: #fff4f3; }}
.modified {{ border-color: #d4a440; background: #fffdf5; }}
mark {{ background: #cbefdb; color: #11683e; padding: 1px 2px; border-radius: 2px; }}
del {{ background: #ffe0de; color: #aa3131; text-decoration: line-through; padding: 1px 2px; }}
.diff-footnote {{ margin-top: 28px; color: #7d8894; font-size: 16px; line-height: 1.7; }}
.report-footer {{ margin-top: 20px; padding: 15px; background: #f0f0f0;
    color: #777; text-align: center; font-size: 20px; line-height: 1.6; overflow-wrap: anywhere; }}
</style></head><body><main class="beta-diff">
<div class="diff-heading"><h1>体服更新 · 左右对照</h1>
<p class="metadata">{escape(diff.title)} · {escape(diff.update_time)} · 版本 {escape(diff.client_version)}</p>
<p class="metadata">检测时间：{escape(diff.recorded_at)} · {len(diff.sections)} 个章节有变化</p>
{compared}<div class="legend"><span><mark>绿色：新增内容</mark></span>
<span><del>红色删除线：删除内容</del></span></div></div>
{''.join(sections)}
<div class="diff-footnote">仅展示本次变化涉及的章节；灰色文字为章节内未变化的上下文。<br>
差异对比上一份已记录的公告正文。完整公告请查看推送中的官网链接。</div>
<footer class="report-footer">{footer_text}</footer>
</main></body></html>"""
