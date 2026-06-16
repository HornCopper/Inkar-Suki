# Worklog

This file records repository changes made in this fork. Keep entries newest first.

Every code, documentation, configuration, dependency, asset, or workflow change should update this file before handoff.

## 2026-06-16 - Equipment Rating Cross-Repo Regression Validation

- Branch: rating
- Type: validation
- Files changed:
  - worklog.md
- Summary:
  - Re-ran bot-side validation after the equipment-rating loop-list and T-heart-method changes.
  - Calculator-side function smoke tests confirmed public/custom loop selection and T-heart-method crystal banquet handling; detailed timing and selected JCL records are logged in the calculator worklog.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
  - Ran `git diff --cached --check`; no whitespace errors.
- Follow-ups / Risks:
  - No OneBot/NapCat end-to-end command run was performed in this validation pass.

## 2026-06-16 - Tank Crystal Banquet All-Attribute Codes

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/base.py
  - worklog.md
- Summary:
  - Corrected T-heart-method full-income feast selection so `风语·水晶芙蓉宴` contributes all five attribute feast codes instead of only the current main-attribute entry.
  - Kept non-T heart methods on the original physics/magic attack banquet selection.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\base.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Running bot processes need restart/reload before calculator command income assembly uses the new feast code list.

## 2026-06-16 - Equipment Rating Player Lookup Alignment

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Aligned equipment-rating role-name lookup with the calculator command by resolving role names through `search_player(role_name, server_name)` instead of the role-name/role-id mixed local lookup path.
  - Kept numeric arguments on the role ID lookup path so `装备评级 <区服> <数字>` can still fall back to magic-box pzid handling when no player is found.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Numeric-only role names remain ambiguous by design because the command treats them as role IDs before pzid fallback.

## 2026-06-16 - Equipment Rating Kungfu List Calculator Consistency

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Restored the bare equipment-rating heart-method selection flow to match the calculator command: resolve player, refresh Tuilan equipment, then build the cached PVE heart-method candidate list.
  - Recomputed each candidate's auto-selected PVE tag while formatting options, matching the calculator command's option-building behavior.
  - This supersedes the prior cache-first latency optimization for the candidate list; the visible delay is the expected Tuilan refresh before showing candidates.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - The candidate list can still be delayed by Tuilan/network latency, same as the calculator command.

## 2026-06-16 - Equipment Rating Kungfu List Latency

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Reduced latency before returning the bare `装备评级 <区服> <角色> 评级列表` heart-method selection list.
  - Player identity resolution for the initial heart-method selection now avoids an eager Tuilan equipment refresh and uses cached PVE equipment first.
  - If no cached PVE equipment is available, the command refreshes Tuilan once and retries; final calculation payload construction still refreshes equipment as before.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - If cached PVE equipment is stale but present, the initial heart-method list may reflect cache until final calculation refreshes the selected equipment.

## 2026-06-16 - Shared Calculator Loop Selection Helper

- Branch: rating
- Type: refactor
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/plugins/jx3/calculator/loop_selection.py
  - worklog.md
- Summary:
  - Extracted shared calculator loop-list helpers into `loop_selection.py`.
  - Reused the same helper for calculator, timeline/compare/kline, equipment compare, and equipment-rating `评级列表` flows so public/custom loop merging and sectioned display stay consistent.
  - Kept equipment-rating-specific error text and prompt text as wrapper parameters while sharing the list data shape.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\loop_selection.py src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Refactor-only change; no endpoint contract change.

## 2026-06-16 - JCL Analysis Help LNX Order

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Moved the `【LNX-】鲁念雪 每阶段减伤/治疗/化解贡献统计` entry in `jcl分析 help` directly under the `BLA-` entry.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
  - Confirmed the help text order is now `BLA-` then `LNX-` then `ASN-`.
- Follow-ups / Risks:
  - Text-only help ordering change; no runtime analyzer behavior changed.

## 2026-06-16 - Equipment Rating Help Examples

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added concrete examples to the `装备评级 help` usage steps for role-name rating, rating-loop list selection, and JX3BOX pzid rating.
  - Removed the explicit heart-method example from the help image to keep the example list shorter.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - No rendered help image was generated in this shell.

## 2026-06-16 - Equipment Rating Calculator Loop List Alignment

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed `装备评级 ... 评级列表` to build its loop selection from the same calculator loop source rules as the calculator command.
  - When the user's calculator source preference is `自定义`, the list now includes both `公有循环` and `自定义循环` sections; otherwise it keeps the public-loop-only list.
  - The selected loop is sent to calculator as `jcl_loop` with `weapon`、`haste`、`loop` and `user_id`, so private/custom loop selections can be calculated by equipment rating instead of being treated as public JCL indices.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires the paired calculator change that accepts optional `jcl_loop` on `/equipment_rating`; older calculator services will ignore this field and cannot calculate custom loop selections correctly.

## 2026-06-16 - Tank Vitality Conversion Rating Panel

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added a T-heart-method-only equipment-rating sidebar panel for vitality conversion.
  - The panel uses the calculator summary's full-income `BaseVitality`, floors `BaseVitality / 3310` as the displayed buff stack count, caps the result at 100 stacks, and shows full buffed base vitality, effective threshold base vitality, and distance to the next stack.
  - The panel title is `增益层数`; the panel now uses a large centered stack count with a `满增益基础体质 / 3,310 向下取整` formula line, followed by left-sidebar-aligned rows for full buffed base vitality, effective base vitality, and distance to the next stack.
  - The T panel replaces the previous heart-method combat distribution block; non-T heart methods still show the existing distribution chart when available.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
  - Attempted a minimal Jinja template render, but the system Python in this shell does not have `jinja2` installed.
- Follow-ups / Risks:
  - No visual render or live equipment-rating command was run in this shell; final layout should be verified with a real T-heart-method rating image in the bot runtime.

## 2026-06-16 - Tank Crystal Banquet Calculator Incomes

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/base.py
  - worklog.md
- Summary:
  - Changed calculator full-income consumable assembly so T heart methods use the corresponding `风语·水晶芙蓉宴` feast code instead of the previous physics/magic attack banquet.
  - Kept main-attribute food/medicine, physics/magic ingots, and shared feasts (`同泽宴`、`百炼水煮鱼`) unchanged.
  - Non-T heart methods continue to use the original physics/magic attack banquet selection.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\base.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran a stubbed file-level assertion for `get_calculator_income_codes`: 铁牢律 includes `FY_CRYSTAL_BANQUET_VITALITY` and excludes `FYYD_PHYSICS`/`FYYD_MAGIC`; 剑纯 still includes `FYYD_PHYSICS`; 气纯 still includes `FYYD_MAGIC`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Direct runtime import through the bot package was not available in this shell because `pdm` is not on PATH and the system Python lacks runtime dependencies such as `yaml`; the targeted assertion used minimal stubs for unrelated imports.

## 2026-06-16 - Equipment Rating ID Compatibility

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed bare `装备评级 <区服> <角色ID>` handling to follow the calculator-style PVE kungfu selection flow: multiple cached PVE kungfus return a selection list, while non-multiple cases continue directly with the default rating JCL.
  - Added 魔盒配装 ID handling for `装备评级 <配装ID>` and `装备评级 <配装ID> 评级列表`, using the same JX3BOX import path as the calculator command.
  - For ambiguous `装备评级 <区服> <数字>` input, preserved the original role-ID path first and falls back to 魔盒配装 ID only when the role cannot be resolved.
  - Kept the existing explicit `装备评级 <区服> <角色ID> <心法>` path unchanged.
  - Preserved `评级列表` behavior so bare ID selection first resolves the kungfu when needed, then returns the public JCL loop list before calculation.
  - Updated the `提交属性` success reply so supported heart methods now recommend `装备评级 <区服> <角色ID>`, with explicit current-heart-method and public-JCL variants on following lines.
  - Updated calculator/equipment-rating help text to show the optional heart-method, 魔盒配装 ID, and `评级列表` arguments.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m py_compile src\plugins\jx3\attributes\__init__.py src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - No live OneBot/calculator endpoint verification was run in this turn; final behavior still depends on local player cache, 推栏装备 fetch, JX3BOX配装接口, and the calculator service being available.

## 2026-06-16 - Upstream Sync For Rating Branch

- Branch: rating
- Type: upstream sync
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/plugins/manage/__init__.py
  - src/utils/permission.py
  - worklog.md
- Summary:
  - Fetched `upstream/main` and fast-forwarded local `rating` from `58f41d83` to `53da5552`.
  - Confirmed local `rating` had no extra commits or uncommitted tracked changes before merging, so no fork-only code needed conflict handling.
  - Brought in upstream calculator PVE tag auto-selection changes, equipment rating tank/DPS option handling, and stricter permission node validation/inspection commands.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - No local runtime bot verification was run; behavior that depends on OneBot/JX3 services still needs live-environment validation if required.

## 2026-06-13 - LNX Report Avatar Branding

- Branch: rating
- Type: change
- Files changed:
  - src/assets/image/jx3/calculator/lnx_mark.png
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Added a local LNX avatar asset for report branding.
  - Replaced the top-right plain `LNX 分析` badge with a rounded avatar mark and label.
  - Added a low-opacity LNX watermark to each Phase card.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
  - Rendered `src/cache/lnx_result_test.png` from the fixed `result.json` sample and visually verified the top avatar mark and low-opacity Phase watermark.
- Follow-ups / Risks:
  - The watermark is intentionally low opacity to avoid competing with table values.

## 2026-06-12 - LNX Buff Detail Pie Panels

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Increased LNX report table text size for better readability.
  - Narrowed the 减伤 Buff 明细 source column and applied ellipsis to long source names.
  - Added three right-side Rose Chart panels beside the 减伤 Buff 明细 table: 减伤贡献 Top 5, 治疗贡献 Top 5, and 化解占总贡献.
  - Rendered equal-angle Rose Chart slices with radius scaled by contribution value, placed kungfu icon, short role ID, and percentage around the chart, colored each label capsule with its matching slice color, and connected each label from its chart-facing edge to the matching slice with softer curved arrows.
  - Removed the bottom pie legend so the chart itself carries the identity mapping.
  - Renamed the report title to 鲁念雪-雷元归枢-JCL贡献统计.
  - Added rounded in-cell contribution bars for 加权贡献、加权总贡献、加权减伤、加权治疗 values, normalized per displayed table column.
  - Kept Wave 加权总贡献与化解总量 at the bottom as the two-row card matrix.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
  - Rendered `src/cache/lnx_result_test.png` from the fixed `result.json` sample and visually verified the larger font, narrower source column, right-side Rose Charts with more dispersed matching-color outer kungfu/role labels and curved arrows, rounded contribution bars, and bottom Wave matrix.
- Follow-ups / Risks:
  - Rose Chart labels intentionally use shortened role names to keep the right-side panel stable.

## 2026-06-12 - LNX Three Contribution Tables Compact

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Changed the LNX contribution layout so 综合贡献、减伤贡献、治疗贡献 tables display on the same row.
  - Added contribution-table-only compact styling with narrower role columns, smaller icons, and ellipsis for long role names.
  - Kept Buff details and Wave summary layout unchanged.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png` and visually verified the three contribution tables share one row with narrower role columns.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Long role names are truncated in the three contribution tables to preserve the same-row layout.

## 2026-06-12 - Merge Upstream Main Into Rating

- Branch: rating
- Type: merge
- Files changed:
  - src/assets/image/subscribes/Chalkboard_Board.png
  - src/assets/source/permission/node.json
  - src/assets/source/subscribe/options.json
  - src/plugins/jx3/__init__.py
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/plugins/jx3/joy/__init__.py
  - src/plugins/jx3/parse.py
  - src/plugins/jx3/rank/rank.py
  - src/plugins/jx3/rank/team_rank.py
  - src/plugins/manage/__init__.py
  - src/plugins/twenty_four/__init__.py
  - src/plugins/twenty_four/process.py
  - worklog.md
- Summary:
  - Merged upstream `main` updates into the `rating` branch.
  - Resolved the calculator command registration conflict by keeping the local LNX and K-line commands while preserving upstream's matcher layout and calculator command updates.
  - Brought in upstream JX3 command, permission, equipment rating, attribute, subscription asset, rank, manage, and twenty-four plugin updates.
  - Removed an upstream trailing whitespace in `src/plugins/jx3/parse.py` so `git diff --check` passes.
- Validation:
  - `pdm run python -m compileall bot.py config.py src` could not run because `pdm` was not available in the local PATH.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
  - Ran `git diff --cached --check`.
- Follow-ups / Risks:
  - OneBot/runtime behavior was not exercised locally because no live adapter session was configured for this merge.

## 2026-06-12 - LNX Wave Matrix Display

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Changed the LNX wave summary from per-card `总贡/化解` labels to a two-row matrix with row labels `总贡献` and `化解`.
  - Kept contribution table titles fixed as `Top 10`; if fewer than 10 rows exist, only the available rows are displayed.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png` and verified the two-row wave matrix plus fixed Top 10 titles.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Phase 1 healing currently has 9 positive contributors in the sample, so the fixed `治疗贡献 Top 10` title displays 9 rows.

## 2026-06-12 - LNX Wave Base Mitigation Contribution

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Changed LNX mitigation contribution to use each wave's maximum restored vulnerable damage as `wave_base_damage`.
  - Mitigation Buff contribution now uses `wave_base_damage * percent`, so 100% reductions such as `镇山河` keep their theoretical contribution even when a target has zero observed post-reduction damage.
  - Verified `镇山河` contribution appears in the sample: Phase 2 weighted `5282.53万`, Phase 4 weighted `8878.81万`.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Recomputed `镇山河` from `result.json`: Phase 2 weighted `5282.53万`, Phase 4 weighted `8878.81万`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Wave-level base damage intentionally applies the same theoretical damage pressure to all targets in the same wave.

## 2026-06-12 - LNX Table Layout Rollback

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Reverted the experimental compact table layout for the LNX report.
  - Removed fixed table classes, fixed column widths, and table-layout overrides while keeping the latest calculation and Top 10 layout behavior.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Table columns are back to the previous full-width layout; a different compacting approach can be tried later.

## 2026-06-12 - LNX Vulnerable Damage Bound

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Tightened the LNX raw-damage restoration filter from `raw_damage <= 300万` to `raw_damage * vulnerability_multiplier <= 220万`.
  - Magnetic-vulnerability waves now effectively use a lower raw base cap of `220万 / 1.3`.
  - Updated the fallback cap to preserve the same vulnerable-damage upper bound.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Checked the full `result.json` sample: no restored `D_vulnerable` exceeded `220万`; the maximum was `220.0万`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - This remains a heuristic for interval coverage ambiguity until damage-instant buff timing is available.

## 2026-06-12 - LNX Raw Damage Upper Bound Filter

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Added a `300万` upper bound filter for LNX restored raw damage.
  - Raw damage restoration now tries positive reductions from high to low and uses the first reduction that keeps restored raw damage within the bound; otherwise it falls back to no positive reduction.
  - Preserved observed `max_reduction_percent` and added `selected_reduction_percent` so diagnostics can distinguish observed coverage from the reduction actually used for restoration.
  - Verified Phase 1 W3 for `罐梨脆栀柿·天鹅坪` skips `守如山 80%` because it would restore `528.88万`, then selects `30%` and restores `151.11万`.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Recomputed Phase 1 W3 `罐梨脆栀柿·天鹅坪` from `result.json`: observed reductions were `80/30/20/15/15`, selected `30%`, and restored raw damage was `151.11万`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - This is a heuristic for interval coverage ambiguity. If later JSON includes damage-instant buff timing, replace this filter with exact event matching.

## 2026-06-12 - LNX Mitigation Wave Base Fix

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Changed LNX mitigation contribution calculation to use the target player's current-wave restored `raw_damage` as the contribution base.
  - Stopped using the player's per-phase maximum default raw damage as the mitigation base, which inflated long-duration reductions by applying one wave's peak damage to every covered wave.
  - Verified Phase 1 `守如山` changed from the inflated `1522.74万` weighted contribution to `462.78万` weighted contribution on the fixed sample.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Recomputed Phase 1 `守如山` from `result.json`: fixed weighted contribution is `462.78万`, compared with the previous inflated `1522.74万`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png` and visually verified the updated rankings and wave cards.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - This changes LNX mitigation rankings because repeated coverage now follows actual wave pressure instead of phase peak pressure.

## 2026-06-12 - LNX Wave Totals And Split Top10 Layout

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Restored per-wave weighted total contribution display in LNX wave cards while keeping absorb/化解 totals as a labeled secondary line.
  - Limited the LNX mitigation and healing contribution tables to Top 10 rows, matching the comprehensive contribution table behavior.
  - Changed the contribution table layout so 综合贡献 Top 10 is shown on its own row, with 减伤贡献 Top 10 and 治疗贡献 Top 10 sharing the next row.
  - Updated LNX wave card labels so total contribution and absorb totals are explicit.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\_template.py src\plugins\jx3\calculator\jcl_analyze.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png` and visually verified the split Top 10 layout plus wave total/absorb labels.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Wave total contribution is the weighted total for the wave and includes mitigation, healing, and absorb contributions.

## 2026-06-12 - LNX Compact Three Table Layout

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - worklog.md
- Summary:
  - Further tightened the LNX report canvas, phase card spacing, table padding, font size, rank width, role icon size, and role text wrapping.
  - Adjusted the three-table grid proportions so 综合贡献、减伤贡献、治疗贡献 stay on one compact row.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\_template.py src\plugins\jx3\calculator\jcl_analyze.py`.
  - Rendered a local LNX sample image from `result.json` to `src/cache/lnx_result_test.png` and visually verified the three contribution tables stay on one compact row.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Very long names can wrap inside the role column; this is intentional to keep the three-table row from expanding.

## 2026-06-12 - LNX Three Table Row Layout

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Changed each LNX phase block to place 综合贡献、减伤贡献、治疗贡献 tables in one row.
  - Tightened table padding, font size, rank width, and role icon/role column sizing to fit the three-table layout.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Rendered a local LNX sample image from `result.json` to verify the three contribution tables fit on one row.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Long player names may still widen role columns; if this becomes an issue, add truncation or controlled wrapping.

## 2026-06-12 - LNX Hide All Raw Columns

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Removed all displayed `未加权` columns from the LNX report tables.
  - Raw contribution values remain in the calculation data for internal/debug use; report sorting and display use weighted contribution.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py`.
  - Rendered a local LNX sample image from `result.json` to verify raw columns are hidden.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - No calculation behavior changed.

## 2026-06-12 - LNX Wave Absorb Display

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Changed the LNX wave summary cards to show only weighted absorb/化解 totals.
  - Renamed the section from `Wave 加权贡献与化解总量` to `Wave 化解总量`.
  - Kept wave total weighted contribution in calculation data for internal use; it is no longer displayed in the wave cards.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py`.
  - Rendered a local LNX sample image from `result.json` to verify the wave cards now show absorb totals only.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - No calculation behavior changed.

## 2026-06-12 - LNX Hide Raw Total Column

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Removed the `未加权总计` column from the LNX 综合贡献 Top 10 table.
  - Kept raw contribution data in the calculation result for internal/debug use; only the table display changed.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - No calculation behavior changed.

## 2026-06-12 - LNX Role Column Alignment

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - worklog.md
- Summary:
  - Restored LNX report role cells to left alignment while keeping table headers and numeric columns centered.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\_template.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - No calculation behavior changed.

## 2026-06-12 - LNX Report Layout Adjustment

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Removed the four top metric cards from each LNX phase block.
  - Changed the 综合贡献 table to display only Top 10 by `weighted_contribution`.
  - Centered LNX report table headers, values, and role cells.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\_template.py`.
  - Rendered a local LNX sample image from `result.json` to verify the layout update visually.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ upload flow was not tested because it requires the running bot adapter and the first-step `/lnx_analyze` endpoint.

## 2026-06-12 - LNX JCL Contribution Analysis

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/_template.py
  - src/plugins/jx3/calculator/jcl_analyze.py
  - worklog.md
- Summary:
  - Added `LNX-` upload prefix support for 鲁念雪 JCL analysis.
  - Added LNX contribution calculation helpers that consume the fixed result JSON structure, restore per-player per-phase default raw damage, calculate mitigation/healing/absorb contributions, apply per-phase time weighting with `r=0.3`, and sort by `weighted_contribution`.
  - Added a single-image LNX report template that combines all phases, displays complete weighted contribution tables, mitigation Buff details, and wave absorb totals.
  - `LNXAnalyze` now calls the future `/lnx_analyze` endpoint on `Config.jx3.api.cqc_url` and renders the returned JSON.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\_template.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched local files, with no whitespace errors.
  - Used `C:\Users\24535\Documents\Tencent Files\245356865\FileRecv\result.json` to build LNX analysis data in the project virtualenv after `nonebot.init()`: 4 phases, 11 waves each.
  - Rendered a local sample image to `src/cache/lnx_result_test.png` and visually checked that all 4 phases are combined into one report.
- Follow-ups / Risks:
  - Live QQ upload flow was not tested because it requires the running bot adapter and the first-step `/lnx_analyze` service endpoint, which is not yet synced to main.
  - The generated sample PNG is under ignored cache and is not part of the code change.
  - The report displays complete lists; very large future logs may produce a tall image and require layout tuning.

## 2026-06-12 - K-Line Game History Window

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Limited the `循环K线游戏` chart to the latest 120 seconds of history.
  - The game still keeps absolute current time for pricing, expiry, and settlement, but the displayed candles are sliced from `(current_time - 120, current_time]` and remapped onto a `0..120s` chart axis.
  - Added a game chart subtitle showing the visible recent window length.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ image rendering was not tested because it requires the running bot adapter and calculator service.

## 2026-06-12 - K-Line Game Exercise Text

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Clarified K-line game settlement output for out-of-the-money options.
  - Call/put payoff logic remains `max(intrinsic, 0)`, but expired out-of-the-money positions now display `放弃行权，行权收入=0` instead of the generic exercise-income text.
  - K/expiry/payoff values continue using the existing compact `万` formatting.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ interaction was not tested because it requires the running bot adapter.

## 2026-06-12 - K-Line Game Invalid Input Exit

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added consecutive format-error tracking for `循环K线游戏`.
  - Empty input, malformed actions, missing call/put type, and invalid quantities now increment `format_error_streak`.
  - Any valid operation or non-format game-state error resets the streak; reaching 3 consecutive format errors automatically exits the game.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ interaction was not tested because it requires the running bot adapter.

## 2026-06-12 - K-Line Game Random Option Terms

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed the K-line option game from a fixed 15-second expiry to a per-decision random term.
  - Each decision point now rolls one of `15/30/45/60` seconds for the at-the-money option, displays the current `T` and expiry time, and uses that term for buy price, expiry jump, settlement, and mark-to-market time value.
  - Future timeline data is checked before mutating cash or positions so a failed JCL append cannot leave the account in a partially changed state.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ image rendering and multi-round gameplay were not tested because they require the running bot adapter and calculator service.

## 2026-06-11 - K-Line Game Display Cleanup

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Removed random JCL source details from the K-line game image.
  - Game mode now shows only game-facing labels: option account, target price, cash, time, positions, expiry model, and price K-line.
  - Header, legend, stat card title, and K-line subtitle no longer expose provider, loop name, haste, character/server, kungfu, or internal source labels.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ image rendering was not tested because it requires the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline K-Line Option Game

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added `循环k线游戏` / `循环K线游戏`.
  - The game starts with 1,000,000 cash, uses rolling DPS close as the underlying price, and offers at-the-money call/put options with `K=P(t)`, `premium=P(t)*3%`, and `T=15s`.
  - Random public JCL segments are fetched from calculator and concatenated directly without price normalization; when future data is insufficient, another JCL is appended.
  - Each action jumps to the next expiry and auto-settles expired options. Buying checks cash, selling only closes existing unexpired positions, so cash/positions do not go negative.
  - The game image reuses the exchange-style K-line renderer and shows cash, price, time, and current positions.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires the paired calculator `/kline_game_random_jcl` endpoint.
  - Live QQ interaction and image delivery were not tested because they require the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline K-Line Axis Spacing

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added right-edge tick label avoidance for the K-line time axis.
  - Regular 15-second ticks close to the terminal battle-time label are hidden so the final labels do not overlap.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live image rendering was not tested in this turn because it requires the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline K-Line Exchange Style

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed K-line rendering to aggregate display candles only when the horizontal time range is long; short timelines keep one-second candles.
  - Long timelines now choose a stepped display interval based on a target candle count, reducing visual density and increasing candle spacing.
  - Updated the standalone `循环K线` image to use a full dark exchange-style layout instead of a light report page with an embedded dark chart.
  - Kept the underlying rolling DPS calculation unchanged; the aggregation is display-only.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live image rendering was not tested in this turn because it requires the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline Rolling Window 10s

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed the default K-line rolling DPS window from 5 seconds to 10 seconds.
  - The bot now sends `rolling_window=10` to `/damage_timeline` and public-loop preview requests.
  - Updated the `循环K线` help text to describe the 10-second rolling DPS K-line.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires the paired calculator default/contract change for callers that omit `rolling_window`.
  - Live QQ image delivery was not tested because it requires the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline K-Line MA Lines

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Expanded the K-line moving average overlay from MA5 only to MA5, MA10, and MA20.
  - Each MA line is calculated from candle close prices and rendered with a separate color and label.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live image rendering was not tested in this turn because it requires the running bot adapter and calculator service.

## 2026-06-11 - Separate Damage Timeline K-Line Command

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added `循环k线` / `循环K线` as a standalone command with the same argument parsing and loop selection flow as `循环曲线`.
  - Moved the K-line panel out of `循环曲线`; the curve command now renders only the damage-bin chart and cumulative DPS chart.
  - The new K-line command renders the black-background K-line panel and summary cards for a single selected loop.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live QQ image delivery was not tested because it requires the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline Rolling Window 5s

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed the default K-line rolling DPS window from 2.5 seconds to 5 seconds.
  - The bot now sends `rolling_window=5` to `/damage_timeline` and public-loop preview requests.
  - Updated the timeline help text to describe the 5-second rolling DPS K-line.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires the paired calculator default/contract change for callers that omit `rolling_window`.
  - Live QQ image delivery was not tested because it requires the running bot adapter and calculator service.

## 2026-06-11 - Damage Timeline K-Line Prototype

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added a single-loop black-background `循环K线 · 2.5秒滚动DPS` panel to the existing damage timeline image.
  - The panel renders red/green candlesticks from calculator `rolling_dps_candles`, a close-price MA5 line, buff overlays, and `Close-Open` momentum bars around a zero axis.
  - `循环对比` keeps the existing comparison charts only, avoiding overlapping multiple candlestick series.
  - The bot now sends `rolling_window=2.5` to `/damage_timeline` and public-loop preview requests.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires a paired calculator that returns `rolling_dps_candles`; old calculator responses simply omit the K-line panel.
  - Live QQ image delivery was not tested because it requires the running bot adapter and calculator service.

## 2026-06-10 - Equipment Rating Ring Combo Note

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added a small per-ring note for calculator `combination_recommendations`.
  - The best positive ring pair is displayed under both ring rows as `戒指最优组合[...]：+DPS`.
  - Kept the existing single-slot best note and slot scoring unchanged.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
  - Rendered `src/templates/jx3/equipment_rating.html` with Jinja2 in the project `.venv` and confirmed the note text is present.
  - Ran `git diff --check`; Git reported LF-to-CRLF warnings for touched files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires calculator responses that include `combination_recommendations`; old responses simply leave the extra note blank.
  - Live QQ image delivery was not tested because it requires the running bot adapter.

## 2026-06-05 - User Loop Rename Command

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added `循环改名` / `改循环名` / `修改循环名` / `变更循环名字` for renaming user-provided calculator loop JCL names.
  - Normal users can rename their own public/private loop files; bot owners can target another user with `循环改名 <QQ号> <心法名>`.
  - Updated `自定义循环 help` and `公有循环审批 help` with the rename command and scope.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported an LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
- Follow-ups / Risks:
  - Requires paired calculator endpoints `/renameable_loops` and `/rename_loop`.
  - Live OneBot rename interaction was not tested because it requires a running adapter and calculator service.

## 2026-06-05 - Public Loop Approval Kungfu Equipment Config

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed public-loop approval preview equipment from one global setting to per-kungfu settings.
  - Approval preview now uses a configured equipment source only when the pending loop's kungfu has a matching setting; otherwise it falls back to the JCL embedded equipment.
  - Updated `公有循环审批 help` and `公有循环审批设置` examples to require `装备 <心法名> ...`, with `装备 <心法名> JCL` restoring the default fallback for that kungfu.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Existing runtime config with the old global `preview_equipment` key is intentionally not used as a cross-kungfu default after this change.
  - Live OneBot approval preview was not tested because it requires a running adapter, approval group context, and calculator service.

## 2026-06-05 - Public Loop Approval Help Index

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Expanded `公有循环审批 help` into a consolidated command index for the whole public-loop workflow.
  - Included user submission commands, approval preview/confirm commands, and bot-owner approval configuration commands in one help response.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - This is help-text only; live command rendering was not separately exercised.

## 2026-06-05 - Public Loop Approval Preview Confirm

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed `公有循环审批` from direct approval to a two-step flow: selecting a pending loop now generates a loop timeline preview, then asks for `Y/N`.
  - `Y` approves and moves the loop into the public loop library; `N` rejects and removes the pending marker without deleting the user's private JCL.
  - Extended `公有循环审批设置` so bot owners can configure preview equipment as JCL embedded gear, a named player, or a JX3BOX pzid.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires paired calculator changes for `/preview_public_loop` and `/reject_public_loop`.
  - Live OneBot confirmation flow and screenshot delivery were not tested because they require a running adapter and approval group context.

## 2026-06-05 - Configurable Public Loop Approval

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Replaced the hardcoded public-loop approval group usage with local runtime config stored at `src/data/jx3/public_loop_approval.json`, defaulting to the existing group `1018743771`.
  - Added `公有循环审批设置` / `公有循环审批配置` for bot owners to view config, set the approval group, and add or remove QQ users with approval permission.
  - Updated approval checks so configured approvers, the approval group owner, and bot owners can approve pending public loops inside the configured approval group.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Live permission checks and group message delivery were not tested because they require a running OneBot adapter and real QQ group context.

## 2026-06-05 - Public Loop Submission Approval

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added `提交公有循环` for users to list their custom calculator loops, select one, and submit it for public-loop approval.
  - Added `公有循环审批` / `审批公有循环` for the owner of QQ group `1018743771` to list pending submissions and approve one by sequence number.
  - Sends the approval group a Chinese notification when a user newly submits a loop, and updates the custom-loop help image with the public submission workflow.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Requires the paired calculator API changes and a calculator restart before the new commands can submit, list, and approve loops.
  - Live OneBot group message delivery was not tested because it requires a running bot adapter in QQ group `1018743771`.

## 2026-06-05 - Equipment Rating Haste Formula Help

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added `加速惩罚与补偿` to the HTML/MathJax `装备评级 help` image.
  - Documented the required/actual haste delta, missing-haste penalty coefficient, overflow-haste compensation coefficient, and adjusted DPS formula.
  - Increased the help screenshot viewport height to fit the added formula section.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `_render_equipment_rating_help_image()` after `nonebot.init()` and `ScreenshotGenerator.launch()`; it returned a `MessageSegment` image.
  - Visually checked the generated cache PNG and confirmed the new haste correction formulas render as mathematical notation.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - The coefficient text mirrors calculator `utils/haste_adjustment.py`; update the help image together with calculator-side coefficient changes.

## 2026-06-05 - Equipment Rating Help Image Wrapper

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Fixed the `装备评级 help` wrapper guard returning the old plain-text usage prompt.
  - The wrapper now returns the same HTML/MathJax-rendered help image as the equipment rating module.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `_render_equipment_rating_help_image()` after `nonebot.init()` and `ScreenshotGenerator.launch()`; it returned a `MessageSegment` image.
  - Ran `rg` to confirm the equipment rating wrapper now calls `_render_equipment_rating_help_image()` instead of returning `EQUIPMENT_RATING_USAGE`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - The help image still depends on MathJax CDN availability during rendering.

## 2026-06-05 - Equipment Rating Result Method Removal

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed the `评级口径` explanation block from the rendered equipment rating result image.
  - Kept the dedicated `装备评级 help` HTML/LaTeX explanation image unchanged.
- Validation:
  - Rendered `src/templates/jx3/equipment_rating.html` with `.venv\Scripts\python.exe` and Jinja2 using a minimal context.
  - Ran `rg` against the result template and confirmed `rating-method` / `评级口径` / `总评公式` no longer appear.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
- Follow-ups / Risks:
  - Users need to use `装备评级 help` to see the full rating formula explanation.

## 2026-06-05 - Equipment Rating Help Index

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added a direct help-argument guard in the `装备评级` matcher wrapper before delegating to `equipment_rating.py`.
  - This keeps `装备评级 help` behavior unchanged while making the command visible to the `inkar help` AST discovery scan.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings across dirty local files, with no whitespace errors.
  - Ran a standalone AST scanner check matching `inkar help` logic and confirmed `提交属性 help`, `装备评级 help`, and `计算器 help` are discovered.
- Follow-ups / Risks:
  - Live `inkar help` image rendering was not rerun because it requires the bot's Playwright/runtime environment.

## 2026-06-05 - Equipment Rating Explanation

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Changed `装备评级 help` and empty `装备评级` to return an HTML-rendered help image instead of plain text.
  - Rendered the single-slot formula and weighted total formula with MathJax LaTeX in the help image.
  - Added a compact `评级口径` section to the rendered equipment rating image so the result itself states the formula and interpretation.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Rendered `src/templates/jx3/equipment_rating.html` with `.venv\Scripts\python.exe` and Jinja2 using a minimal context.
  - Ran `_render_equipment_rating_help_image()` after `nonebot.init()` and `ScreenshotGenerator.launch()`; it returned a `MessageSegment` image with MathJax-rendered formulas.
  - Visually checked the generated cache PNG and confirmed formulas rendered as mathematical notation rather than raw LaTeX.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for touched and already-dirty files, with no whitespace errors.
- Follow-ups / Risks:
  - The formula text mirrors the current calculator implementation; update it together with calculator-side scoring changes if that algorithm changes.
  - The help image uses MathJax from jsDelivr during rendering, so the rendered help depends on that CDN being reachable.

## 2026-06-05 - Attribute Missing Role Prompt

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/attributes/v2_remake.py
  - src/plugins/jx3/attributes/v4.py
  - worklog.md
- Summary:
  - Changed `属性` / `查装` missing-role handling to return the equipment submission prompt instead of the old `提交角色` prompt.
  - Applied the same prompt change to explicit `属性v2r` and `属性v4` lookups, because these paths cannot recover world-channel equipment automatically.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for touched and already-dirty files, with no whitespace errors.
- Follow-ups / Risks:
  - This only changes attribute lookup prompts; other JX3 commands that genuinely need a submitted role still use the `提交角色` prompt.

## 2026-06-05 - Attribute Submit Help Index

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - worklog.md
- Summary:
  - Updated `提交属性` help argument handling to accept `help` / `帮助` / `参数` / `示例`.
  - This makes `提交属性 help` match the `inkar help` AST discovery rule, so it appears in the help index automatically.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for `src/plugins/fun/__init__.py`, `src/plugins/jx3/attributes/__init__.py`, and `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Ran a standalone AST scanner check matching `inkar help` logic and confirmed both `提交属性 help` and `计算器 help` are discovered.
- Follow-ups / Risks:
  - Live `inkar help` image rendering was not rerun because it requires the bot's Playwright/runtime environment.

## 2026-06-05 - JCL Analysis Help

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/assets/image/jx3/calculator/jcl_analysis_mingyi_record.jpg
  - worklog.md
- Summary:
  - Added `JCL分析 help` / `JCL分析 帮助` as a short Chinese guide for upload-triggered JCL analysis.
  - Included the provided 茗伊战斗事件记录 screenshot as a stable bot asset instead of depending on the QQ temp path.
  - Listed the supported analysis prefixes and the copied-file ` - 副本` filename suffix reminder.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for `src/plugins/fun/__init__.py` and `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
- Follow-ups / Risks:
  - Live OneBot command verification was not run in this turn; the change is limited to command registration, static text, and a local image asset.

## 2026-06-05 - Calculator Help Command

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/assets/image/jx3/calculator/calculator_equipment_export.jpg
  - worklog.md
- Summary:
  - Added `计算器 help` / `计算器 帮助` handling to the main calculator matcher before normal argument parsing.
  - The help response explains manual equipment submission, 茗伊 export path, calculator prefix usage, equipment rating format, JCL source caveat, and the detailed calculator documentation link.
  - Added the provided 茗伊 equipment export screenshot as a calculator help image attachment.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for `src/plugins/fun/__init__.py` and `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Confirmed the help text, `calculator_equipment_export.jpg` asset reference, help argument interception, and copied image asset are present.
- Follow-ups / Risks:
  - Live bot command verification was not run because it requires a running OneBot adapter.

## 2026-06-05 - Inkar Help Hide Summary Counts

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/fun/__init__.py
  - worklog.md
- Summary:
  - Removed the three summary count cards from the `inkar help` rendered image.
  - Removed the now-unused help entry `type` field that only powered those counters.
  - Kept the header, command grouping, command names, and aliases visible.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for `src/plugins/fun/__init__.py` and `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Ran `Select-String` against `src/plugins/fun/__init__.py` to confirm no `summary`, `entry["type"]`, or `"type":` help-counter rendering remains.
- Follow-ups / Risks:
  - Live `inkar help` image rendering was not rerun because it requires the bot's Playwright/runtime environment.

## 2026-06-05 - Calculator Mixed Loop Sources

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added a shared calculator-loop selection helper that lists both `【公有循环】` and `【自定义循环】` when `计算器来源=自定义`.
  - Applied the mixed-source loop list to `计算器`, `装备对比`, `循环曲线`, and `循环对比`.
  - Selected loops now carry their own `user_id`, so choosing a public loop calculates against the public JCL library and choosing a custom loop calculates against the user's custom JCL library.
  - Tightened loop number validation to reject `0` and negative values in calculator and equipment-compare loop selection.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran a static source check confirming the old `get_loop(event.user_id if is_custom else 0)` pattern is gone and mixed-source helpers are used.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Calculator and equipment-compare behavior now depends on the selected loop source, not only the global `计算器来源` preference.

## 2026-06-05 - Inkar Help Hide Command Paths

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/fun/__init__.py
  - worklog.md
- Summary:
  - Removed the per-command plugin source path from the `inkar help` rendered help cards.
  - Kept command names, aliases, grouping, and summary counts unchanged.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings for `src/plugins/fun/__init__.py` and `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Ran `Select-String` against `src/plugins/fun/__init__.py` to confirm no `entry["source"]`, `class="meta"`, or `.meta` rendering remains.
- Follow-ups / Risks:
  - Live `inkar help` image rendering was not rerun because it requires the bot's Playwright/runtime environment.

## 2026-06-05 - Inkar Help Index

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/fun/__init__.py
  - worklog.md
- Summary:
  - Added `inkar help` / `音卡 help` as an HTML-rendered help index image.
  - The renderer scans `src/plugins/**/*.py` at runtime for `on_command` entries whose command/aliases contain help-like keywords, and for handlers that explicitly support `help` / `帮助` / `参数` / `示例` arguments.
  - The image groups discovered help entries into general help, JX3 help, parameter help, and other help, so newly added help commands following the same patterns appear without editing the renderer list.
  - JX3 plugin-path entries are grouped under `剑三功能` even when they are parameter help entries, and item cards no longer display the `参数帮助` / `独立指令` type label.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran a standalone AST scanner check based on the same rules to confirm current entries include `inkar help`, `自定义循环 help`, `循环曲线 help`, `循环对比 help`, `删除循环 help`, and `删除循环all help`, with JX3-path entries grouped under `剑三功能`.
  - Ran `git diff --check`; Git reported existing LF-to-CRLF warnings, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Local HTML screenshot rendering was not run because this environment lacks Playwright/PDM; runtime rendering depends on the bot's normal Playwright environment.

## 2026-06-05 - Custom Loop Help Export Image

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/assets/image/jx3/calculator/custom_loop_jcl_export.jpg
  - worklog.md
- Summary:
  - Added the provided JCL export method screenshot to the `自定义循环 help` rendered image.
  - Split the help image into explicit sections for making JCL, JCL export method, using custom loops, and deleting custom loops.
  - Added both deletion commands to the help image: `删除循环 <心法名>` for list-based deletion and `删除循环all <心法名>` for deleting all custom loops under one kungfu.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Local screenshot rendering was not rerun because this environment still lacks Playwright/PDM; runtime rendering depends on the bot's normal Playwright environment.

## 2026-06-05 - Custom Loop Delete All By Kungfu

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added `删除循环all <心法名>` as the explicit command for deleting all current-user custom loops for one kungfu.
  - Updated `删除循环` help text and the `自定义循环 help` image copy to mention the new all-by-kungfu deletion command.
  - Kept `删除循环 <心法名>` as the list-based single-loop deletion flow.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Requires the paired calculator `/delete_loop` behavior that treats `all_delete=true` as one-kungfu directory deletion only.

## 2026-06-05 - Custom Loop Delete List

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed `删除循环 <心法名>` to fetch the current user's custom loop list and prompt for numbered selections before deletion.
  - Disabled `删除循环 all` from the bot side and return guidance to delete by list instead.
  - Added custom-loop deletion guidance to the `自定义循环 help` rendered image.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Requires the paired calculator `/delete_loop` single-loop deletion contract; older calculator code still deletes whole directories.

## 2026-06-05 - Custom Loop Help Image

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added the `自定义循环` command with `help` / `帮助` / `参数` / `示例` support.
  - Rendered the custom JCL calculator loop guide as an HTML image, covering setup, wooden dummy recording, filename format, upload, and preference switching.
  - Empty `自定义循环` also returns the same help image; unsupported arguments return `参考格式：自定义循环 help`.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Attempted to render `_render_custom_loop_help_image()` once, but local plain `python` lacks `playwright` and `pdm` is not installed in this environment; screenshot rendering was not locally verified.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - The guide references an external settings picture requested by wording, but no matching image asset was present in the repository; the current image keeps that step as text.

## 2026-06-05 - Damage Timeline Mixed Loop Sources

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - For `循环对比` with `计算器来源=自定义`, the bot now fetches both public and current-user custom loops.
  - The loop selection prompt groups entries under `【公有循环】` and `【自定义循环】` with continuous numbering.
  - Selected timeline loops now carry per-loop `user_id`, so mixed public/custom selections calculate from the correct source.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Requires the paired calculator `/damage_timeline` per-loop `user_id` support for mixed public/custom comparisons.

## 2026-06-05 - Damage Timeline Prefix Case

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Made `循环曲线` and `循环对比` calculator prefixes case-insensitive by generating aliases for all letter-case combinations.
  - Normalized raw command prefixes to uppercase when choosing the calculator tag, so `Jc循环曲线` and `jc循环对比` resolve to the same tag as `JC循环曲线`.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Ran a static alias-generation check confirming `Jc循环曲线`, `jc循环曲线`, and `jC循环对比` are generated.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Existing uppercase aliases remain supported.

## 2026-06-05 - Damage Timeline Hide Provider

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Removed provider display from `循环曲线` and `循环对比` result cards.
  - Kept loop labels, DPS, total damage, battle time, and haste visible.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Confirmed no provider display string remains in `src/plugins/jx3/calculator/__init__.py`.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Calculator response still keeps provider metadata internally; this only hides it from rendered images.

## 2026-06-05 - Damage Timeline Help Example

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Updated `循环曲线` and `循环对比` help examples to use `剑胆琴心 倦收天`.
  - Kept the existing `bin=2.5` and loop-selection examples unchanged.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - None.

## 2026-06-05 - Damage Timeline Curve Help

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added a dedicated `循环曲线` help response for empty input and `帮助` / `参数` / `示例` / `help`.
  - The help text lists role and pzid parameters, optional `bin=<seconds>`, fixed per-second cumulative DPS, and single-loop selection.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - `循环对比` keeps its separate help text and multi-loop selection rules.

## 2026-06-05 - Damage Timeline Empty Command State Fix

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Fixed empty `循环曲线` leaving the matcher waiting for `timeline_loop_order` without timeline state.
  - Empty `循环曲线` now finishes with the timeline argument prompt.
  - Added a defensive state check before finishing timeline rendering, returning a Chinese retry prompt instead of raising `KeyError: timeline_loops`.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Users must re-send the full `循环曲线` / `循环对比` command after an incomplete or stale interaction.

## 2026-06-05 - Merge Upstream Inkar

- Branch: rating
- Type: upstream merge
- Files changed:
  - src/assets/source/jx3/kungfu_formulations.json
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/base.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/plugins/jx3/calculator/jx3box.py
  - src/plugins/jx3/calculator/traverse.py
  - src/plugins/jx3/calculator/universe.py
  - src/plugins/jx3/equip/equip_config.py
  - src/plugins/jx3/joy/__init__.py
  - src/utils/database/attributes.py
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Fetched `upstream/main` and fast-forwarded `rating` from `cdecb596` to `ea203946`.
  - Temporarily stashed local timeline updates before merge and restored them afterward.
  - No merge conflicts occurred; local timeline updates in `src/plugins/jx3/calculator/__init__.py` were preserved.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Branch is now ahead of `origin/rating` by the upstream commits.

## 2026-06-05 - Damage Timeline Full-Height Buff Frames

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed timeline buff overlays from small horizontal-axis bands to full-height translucent chart frames.
  - Buff labels still use the returned row value only to avoid text overlap.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Overlapping full-height frames intentionally stack transparently when multiple full-income buffs are active at the same time.

## 2026-06-05 - Damage Timeline Buff Overlay

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added full-income-only timeline buff overlay rendering for `循环曲线` and `循环对比`.
  - The SVG charts now draw translucent horizontal-axis bands for `号令三军一鼓`, `号令三军二鼓`, `朝圣言`, and `鼎` when calculator returns `buff_overlays`.
  - Non-full-income calculator preferences keep the existing clean chart without buff bands.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Requires the paired calculator `/damage_timeline` response field `buff_overlays`; old calculator responses simply render without bands.

## 2026-06-05 - Damage Timeline Bin Range Help

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Updated the `循环对比` help text to use the requested role and loop-selection examples.
  - Routed invalid `循环对比` argument counts to the same dedicated help text.
  - Tightened optional `bin=<seconds>` validation to the user-facing range `1` to `60`.
  - Kept cumulative real-time DPS independent from `bin`, using the existing per-second data.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran `git diff --check`; Git reported the existing LF-to-CRLF warning for `src/plugins/jx3/calculator/__init__.py`, with no whitespace errors.
  - Checked `worklog.md` for trailing whitespace and conflict markers.
- Follow-ups / Risks:
  - Existing commands with `bin` below `1` second now fail validation by design.

## 2026-06-05 - Damage Timeline Compare Help

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added a `循环对比` help response for empty input and `帮助` / `参数` / `示例` / `help`.
  - The help text lists role and pzid parameters, optional `bin=<seconds>`, the loop-selection format, and concrete examples.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
- Follow-ups / Risks:
  - Empty `循环曲线` still keeps the existing propagation behavior; this change only adds help for `循环对比`.

## 2026-06-05 - Damage Timeline Axis Spacing

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Confirmed cumulative real-time DPS still uses per-second `cumulative_dps_bins`.
  - Added right-side time-domain padding to the SVG charts so the last curve point no longer sits on the right axis edge.
  - Suppressed a regular 15-second tick when it is too close to the terminal-time label, avoiding overlaps such as `225s` and `227.8s`.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - Very short fights still keep the terminal label, so the axis may show fewer regular ticks by design.

## 2026-06-05 - Damage Timeline Bin Argument

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added optional `bin=<seconds>` parsing for `循环曲线` and `循环对比`, for example `循环对比 梦江南 叶凝城 bin=2.5`.
  - The parsed bin size is passed only to calculator `/damage_timeline` as the damage amount bin size; cumulative real-time DPS continues to use per-second data.
  - Kept the default damage bin size at `2.5` seconds and added validation for one `bin` argument in the range `0.1` to `60`.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - Requires the calculator-side floating-point `bin_size` support already added in this branch.

## 2026-06-05 - Damage Timeline Per-Second DPS

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed the cumulative real-time DPS chart to read `adjusted.cumulative_dps_bins`, keeping its sampling interval at 1 second.
  - Left the damage chart on `adjusted.bins`, which remains the 2.5-second damage amount series.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - Requires a calculator response that includes `cumulative_dps_bins`; older calculator responses would not provide the intended per-second DPS chart data.

## 2026-06-05 - Damage Timeline Progress Reply

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - After a valid `循环曲线` or `循环对比` loop selection, the bot now immediately replies `音卡正在努力演算中！` before requesting calculator data and rendering the final image.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - The progress reply is sent only after loop selection validates; invalid selections still finish with the existing error message.

## 2026-06-05 - Damage Timeline Axis Labels

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Renamed the damage chart title from generic bin wording to `每2.5秒伤害量`.
  - Added x-axis time labels at 15-second intervals and an additional terminal-time label based on the longest adjusted battle time.
  - Left `cumulative_dps` data and calculation unchanged.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - Dense/very short fights can still show close labels near the terminal time, but the terminal label is intentionally retained.

## 2026-06-05 - Damage Timeline 2.5s Bin

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Changed `循环曲线` / `循环对比` requests to send `bin_size=2.5` to calculator `/damage_timeline`.
  - Updated chart rendering to handle floating-point `second` values on the x-axis and title the damage chart as `伤害量（2.5 秒 bin）`.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - Requires a calculator instance with floating-point `/damage_timeline` bin support; older calculator code will coerce the value back to an integer.

## 2026-06-05 - Damage Timeline Commands

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added `循环曲线` / `T循环曲线` / `QC循环曲线` / `JC循环曲线` / `TL循环曲线` / `JY循环曲线` / `WX循环曲线` commands that reuse calculator argument parsing, preferences, loop source, and loop selection flow.
  - Added `循环对比` command aliases with the same calculator inputs and support for selecting two or more loops with spaces, half-width commas, or full-width commas.
  - Calls calculator `/damage_timeline`, renders a vertical report image with adjusted-only per-second damage and cumulative DPS curves, and marks the highest per-second damage point on the damage chart.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran lightweight source checks confirming no raw DPS label is visible in the rendered report path and peak labels are present.
- Follow-ups / Risks:
  - End-to-end bot execution still depends on a running calculator service and OneBot environment; if calculator is not restarted, the new `/damage_timeline` route will not exist.

## 2026-05-29 - Screenshot Local HTML Networkidle Timeout

- Branch: rating
- Type: fix
- Files changed:
  - src/utils/generate.py
  - worklog.md
- Summary:
  - Changed screenshot rendering so generated local HTML files no longer wait for Playwright `networkidle`, which can hang on slow or stalled remote images during commands such as `装备评级`.
  - Added a bounded font/image readiness wait for `wait_for_network=True`, so local report images still wait briefly for assets but continue instead of failing after 30 seconds.
  - Made first-use screenshot rendering await Playwright startup instead of launching it in the background and immediately using the browser handle.
- Validation:
  - Ran `python -m py_compile src\utils\generate.py`.
  - Re-rendered the cached failing equipment-rating HTML `src\cache\cf7207cf5b2911f1ba54acf23c25b344.html` through `ScreenshotGenerator`; it completed in 4.07 seconds and wrote `C:\Users\24535\AppData\Local\Temp\inkar_equipment_rating_render_test.png`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check` (only the existing LF/CRLF normalization warning for `src/utils/generate.py`).
- Follow-ups / Risks:
  - Remote equipment/talent icons may still be absent in the final screenshot if their upstream host is unreachable for the bounded wait window, but the command should now return a report image instead of crashing.

## 2026-05-29 - Equipment Rating Dynamic Income Recommendations

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Equipment-rating reports now consume calculator `meta.recommendations` and render recommended 药品增强、食品增强、家园菜、家园酒、香水、阵眼.
  - Moved the recommendation block out of both side/content columns and into the full-width area directly above the talent strip.
  - Added a small formatter that tolerates older calculator responses without recommendation metadata.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
- Follow-ups / Risks:
  - The report display depends on the calculator `/equipment_rating` response including the new recommendation metadata; older calculator instances simply omit these rows.

## 2026-05-28 - Attribute Submit Rating Hint

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - After `提交属性` saves imported equipment data, the success reply now checks whether the submitted kungfu is supported by equipment rating.
  - Supported kungfus append an equipment-rating command hint using the resolved submit server, role name, and kungfu name, e.g. `装备评级 剑胆琴心 倦收天 太虚剑意`.
  - The command hint now prefers the submitted/resolved role name instead of numeric role ID, so local imported records do not expose a generated ID in the reply.
  - The attribute query hint now also uses a complete command, e.g. `属性 剑胆琴心 倦收天`, instead of only mentioning the `属性` command name.
  - Unsupported kungfus now explicitly append `该心法暂不支持装备评级`；calculator support-query failures append an unable-to-confirm hint instead of silently omitting rating status.
  - Fixed the two one-message `提交属性 ... <茗伊装备导出码>` branches so they also use the unified success formatter instead of the old short success text.
  - Added a small public equipment-rating support helper; submit-time support checks use a short timeout and silently skip the hint if calculator is unavailable.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\attributes\__init__.py src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `python -m compileall bot.py config.py src`.
- Follow-ups / Risks:
  - The hint depends on calculator `/equipment_rating/kungfus`; if calculator is stopped or slow, the reply will say it cannot confirm equipment-rating support.

## 2026-05-28 - Preference Item Help Text

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/preferences/app.py
  - worklog.md
- Summary:
  - Updated `偏好 <偏好项>` queries to include the current value, all available values with descriptions, and concrete `偏好 <偏好项> <设定值>` examples.
  - This makes `偏好 计算器增益` show `无增益`、`满增益`、`满增益风雷` and their setting commands directly in the reply.
  - Limited `偏好 计算器阵眼` setting examples to two representative commands while keeping the full available formation list visible.
- Validation:
  - Ran `python -m py_compile src\plugins\preferences\app.py src\plugins\preferences\__init__.py`.
  - Ran `python -m compileall bot.py config.py src`.
- Follow-ups / Risks:
  - The richer help text applies to all single preference item queries, not only calculator income.

## 2026-05-28 - Calculator Full Income Consumables

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/base.py
  - src/plugins/jx3/calculator/__init__.py
  - src/assets/source/preference/preferences.json
  - worklog.md
- Summary:
  - Replaced the normal calculator `满增益` and `满增益风雷` presets with the equipment-rating style full-income environment that also appends main-attribute food/medicine, attack ingot, and feast codes by kungfu.
  - Added a shared income-expansion helper so normal calculator, equipment compare, and equipment traversal use the same per-kungfu consumable list.
  - Updated the preference descriptions to show that the full-income options now include consumables and feast buffs.
- Validation:
  - Ran `python -m compileall bot.py config.py src`.
  - Ran a function-level check for 太虚剑意、无方、明尊琉璃体、铁骨衣, confirming the appended consumables match main attribute and inner/outer type; `无增益` still returns no income codes.
  - Ran `git diff --check` (only LF/CRLF normalization warnings).
- Follow-ups / Risks:
  - Running bot instances need a restart before the new preset expansion is used.

## 2026-05-23 - Calculator Support Command

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added the `计算器支持` command, mirroring `装备评级支持`: empty input lists currently available public calculator kungfus, and `计算器支持 <心法名>` lists that kungfu's available loops.
  - The support list is built from the calculator `/loops` endpoint, so it reflects the currently loaded public loop library instead of only the bot's local kungfu table.
  - Deduplicated supported kungfus by final display name to avoid PC/mobile mapped kungfus appearing twice, and deduplicated displayed loop names in single-kungfu detail output.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check` (only LF/CRLF normalization warning).
- Follow-ups / Risks:
  - If calculator is not running or `jx3.api.calculator_url` is unreachable, the command returns a readable service-unavailable message.

## 2026-05-23 - RD Analyze Support Command

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added the `RD分析支持` command to describe RD group-file analysis support, including `BLA-` single-boss full-fight RHPS/RDPS analysis and `TRD-` Tang Huairen P1 RDPS analysis, required JCL filename format, and an example filename.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\__init__.py`.
  - Ran `git diff --check` (only LF/CRLF normalization warning).
- Follow-ups / Risks:
  - The command is text-only; actual `TRD-` analysis still depends on a valid `jx3.api.bla_url`.

## 2026-05-23 - Revert JCL Analyze Forward URL

- Branch: rating
- Type: revert
- Files changed:
  - src/config/__init__.py
  - src/assets/source/config.yml
  - src/plugins/jx3/calculator/jcl_analyze.py
  - src/plugins/jx3/calculator/rdps.py
  - src/config/config.yml
  - worklog.md
- Summary:
  - Reverted the temporary `jcl_analyze_url` forwarding configuration and restored JCL analysis calls to the prior `cqc_url` / `bla_url` behavior.
  - Removed the local runtime `jcl_analyze_url: "http://10.0.15.4:11223"` entry.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\config\__init__.py src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\rdps.py`.
  - Ran `git diff --check`.
  - Confirmed no remaining git diff in the JCL forwarding files.
- Follow-ups / Risks:
  - `TRD-` again depends on `jx3.api.bla_url`; if it is empty, requests will fail as before.

## 2026-05-23 - JCL Analyze Forward URL

- Branch: rating
- Type: change
- Files changed:
  - src/config/__init__.py
  - src/assets/source/config.yml
  - src/plugins/jx3/calculator/jcl_analyze.py
  - src/plugins/jx3/calculator/rdps.py
  - worklog.md
- Summary:
  - Added `jx3.api.jcl_analyze_url` as an optional dedicated forwarding base URL for group-file JCL analysis requests.
  - Updated CQC/FAL/YXC/ROD/HPS/ASN/THR/THF/LGZ analyzers to use `jcl_analyze_url` first and fall back to the existing `cqc_url`, so intranet-tunnel forwarding can be configured without changing calculator or other API URLs.
  - Updated BLA/TRD analyzers to use the same forwarding URL first and fall back to the existing `bla_url`; `TRD-` still posts to `/jcl_thr_p1`.
  - Added a BLA/TRD URL validation guard so missing or protocol-less forwarding addresses return a readable bot message instead of raising `httpx.UnsupportedProtocol`.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\config\__init__.py src\plugins\jx3\calculator\jcl_analyze.py src\plugins\jx3\calculator\rdps.py`.
  - Ran `git diff --check` (only LF/CRLF normalization warnings).
- Follow-ups / Risks:
  - Runtime `src/config/config.yml` is ignored; deployment needs to add `jcl_analyze_url` there when switching to the tunnel address.

## 2026-05-23 - Equipment Rating Support Usage Example

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added a concrete `装备评级 剑胆琴心 倦收天 剑纯` usage example to the `装备评级支持` supported-kungfu list response.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `git diff --check` (only LF/CRLF normalization warning).
- Follow-ups / Risks:
  - None.

## 2026-05-23 - Equipment Rating Support Detail Cleanup

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Hid the `循环提供者` line from the single-kungfu `装备评级支持 <心法>` response while keeping calculator response data unchanged.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `git diff --check` (only LF/CRLF normalization warning).
- Follow-ups / Risks:
  - None.

## 2026-05-23 - Equipment Rating Help Text

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added `装备评级 help` / `装备评级 帮助` handling and changed empty `装备评级` usage to return guidance instead of a silent finish.
  - Expanded the equipment-rating usage text to show the required first step: `提交属性 <服务器> <角色名> <心法> <茗伊装备导出码>`, followed by rating, public-loop list, and supported-kungfu queries.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `git diff --check` (only LF/CRLF normalization warning).
- Follow-ups / Risks:
  - The example uses a placeholder for the long 茗伊 export code so the bot message stays readable.

## 2026-05-23 - Equipment Rating DPS Distribution

- Branch: rating
- Type: change
- Files changed:
  - tools/precompute_equipment_rating_distribution.py
  - src/assets/source/jx3/equipment_rating_distribution_colors.json
  - src/assets/source/jx3/equipment_rating_distribution.json
  - src/assets/image/jx3/equipment_rating/distribution/*.svg
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added a precompute script that uses the embedded DPS box-plot quantile data, fits per-kungfu Beta distributions on the shared normalized [0, 1] interval, and writes static metadata plus SVG charts.
  - Added a separate kungfu color configuration JSON for the generated distribution charts.
  - Updated equipment rating rendering to load the precomputed distribution index and place the current kungfu highlighted SVG below the enchant-benefit chart; runtime rendering does not fit or draw curves.
  - Tightened the left sidebar header spacing so the added distribution section fits more comfortably.
  - Hid the `化劲` row from the equipment-rating report's left-side detailed attributes.
  - Restored detailed-attribute haste display to `数值 / 段位` without thousands separators after the upstream UI update dropped the suffix.
- Validation:
  - Ran `python tools\precompute_equipment_rating_distribution.py`, generating 23 SVG distribution charts and `equipment_rating_distribution.json`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src tools`.
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered the Jinja template with sample equipment-rating data and confirmed the distribution SVG URI is present.
  - Ran `git diff --check` (only LF/CRLF normalization warnings).
- Follow-ups / Risks:
  - Future distribution data changes require rerunning `tools\precompute_equipment_rating_distribution.py`.
  - The merged `问水诀/山居剑意` distribution is keyed to `10144` as requested.

## 2026-05-22 - Upstream UI Sync

- Branch: rating
- Type: upstream sync
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Fetched `upstream/main` and fast-forwarded local `rating` from `b6782587` to `76748967`.
  - Upstream updated the JX3 equipment rating UI rendering path.
  - No upstream file deletions were present in this sync.
- Validation:
  - Ran `python -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `git diff --check HEAD~1..HEAD`.
  - Ran `git status --short --branch`.
- Follow-ups / Risks:
  - Local `rating` is ahead of `origin/rating`; push when ready.
  - Bot process needs restart before upstream UI changes are visible.

## 2026-05-22 - Equipment Rating PVE Equip Selection

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed equipment rating payload construction to select only PVE cached equipment.
  - Added calculator-style PVE tag selection for special kungfus (`QCPVE`, `JCPVE`, `JYPVE`, `TLPVE`, `WXPVE`) and generic `DPSPVE` / `TPVE` / `HPSPVE`.
  - Added an exact `kungfu_id` and `tag == "PVE"` filter before sending `jcl_data` to calculator.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran a helper check for `_equipment_rating_pve_tag()` special and generic kungfu mappings.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - Users with only PVP/PVX cache for the requested kungfu will now receive a clear PVE equipment missing message.

## 2026-05-22 - Upstream Sync

- Branch: rating
- Type: merge
- Files changed:
  - src/assets/font/fzjz.ttf
  - src/plugins/jx3/attributes/v4.py
  - src/templates/jx3/attributes_v4.html
  - worklog.md
- Summary:
  - Fetched `upstream/main` and merged update `837c4689` into local `rating`.
  - Merge completed without conflicts.
  - Upstream added `fzjz.ttf` and adjusted the JX3 attributes v4 rendering path.
- Validation:
  - Ran `git rev-list --left-right --count HEAD...upstream/main` after merge; local branch is no longer behind upstream (`2 0`).
  - Ran `git status --short --branch`.
- Follow-ups / Risks:
  - Local `rating` now contains a merge commit and is ahead of `origin/rating`; push when ready.

## 2026-05-22 - Equipment Rating Start Prompt

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed the equipment-rating start acknowledgement from `装备评级中，请稍后。` to `装备评级中，请稍等片刻！`.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - Running bot process must restart before the new text is visible.

## 2026-05-22 - Equipment Rating Direct Enchant Income

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Updated the equipment-rating income chart to read calculator-provided `dps_per_enchant` values directly.
  - Removed the old `dps_per_100` enchant-point scaling fallback; old calculator income responses no longer render this chart.
  - Changed embedding chip text to derive from `attribute_key` via the local attribute-short-name mapping, then append `value`, instead of trusting calculator-provided text.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran a direct helper check confirming embedding chips render `无双+978` / `体质+978` from `attribute_key` and that old `dps_per_100`-only income responses return no chart rows.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - Running bot and calculator processes must both restart before the new response/rendering contract is visible.

## 2026-05-22 - Equipment Rating Income Renderer Scope

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Kept the equipment-rating income chart renderer from filtering zero-valued income rows.
  - Left calculator-side income generation unchanged after confirming the current request is to avoid calculator changes.
- Validation:
  - Superseded by the direct calculator-side enchant income implementation above before handoff.
- Follow-ups / Risks:
  - Superseded by the direct calculator-side enchant income implementation above.

## 2026-05-22 - Equipment Rating Six Income Rows

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Stopped filtering near-zero enchant income rows in the equipment-rating report renderer.
  - Ensured calculator-provided zero income values still render, so the chart can consistently show the six expected attributes.
  - Changed zero-valued compact labels from `+0.0` to `+0`.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran a helper check for `_prepare_attribute_incomes()` with two zero-valued income rows and confirmed six rendered rows plus `+0` labels.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - Depends on calculator returning zero-valued `summary.attribute_incomes` rows; running services must restart on both sides.

## 2026-05-22 - Upstream Sync

- Branch: rating
- Type: merge
- Files changed:
  - worklog.md
- Summary:
  - Fetched `upstream/main` and merged it into the local `rating` branch.
  - Upstream update was merge commit `f25f2b0a`; merge completed without conflicts.
  - The resulting local merge commit is `92ce3052`.
- Validation:
  - Ran `git rev-list --left-right --count HEAD...upstream/main`; local branch is no longer behind upstream (`2 0`).
  - Ran `git status --short --branch`.
- Follow-ups / Risks:
  - Local `rating` is ahead of `origin/rating` by 2 commits and has not been pushed.

## 2026-05-22 - Equipment Rating Score Badge Bloom Revert

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed the added rank-colored bloom shadows from the top-right score badge.
  - Restored the badge to the prior subtle shadow-only style.
- Validation:
  - Rendered the equipment-rating template with sample S-rank data and confirmed the bloom shadows are absent.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - None.

## 2026-05-22 - Equipment Rating Score Badge Bloom

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added a subtle rank-colored bloom around the top-right equipment-rating score badge.
  - Kept the score text color, badge layout, and single pale gradient background unchanged.
- Validation:
  - Rendered the equipment-rating template with sample S-rank data and confirmed the bloom shadows are emitted.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A visual check with ACE/S+/A ranks is useful because stronger rank colors may make the bloom more visible.

## 2026-05-22 - Equipment Rating Score Badge Gradient Revert

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Reverted the score badge background from layered radial/multi-stop gradients back to the previous single pale rank-tinted linear gradient.
  - Kept the fixed red score text and rank-colored border/background behavior.
- Validation:
  - Rendered the equipment-rating template with sample S-rank data and confirmed `radial-gradient` is absent.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - None.

## 2026-05-22 - Equipment Rating Score Badge Gradient Polish

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Replaced the score badge's single pale gradient with layered radial highlights and a multi-stop linear gradient.
  - Kept score text colors unchanged while making the rank-tinted badge background transition more naturally.
- Validation:
  - Rendered the equipment-rating template with sample S-rank data and confirmed the layered gradient CSS is emitted.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A visual check is useful for ACE and A ranks because stronger accent hues can look more saturated than S.

## 2026-05-22 - Equipment Rating Score Badge Color Refinement

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Kept the top-right score number fixed red instead of using the rank accent color.
  - Limited rank color theming to the score badge border, pale background, and subtle shadow.
  - Softened the themed border/background opacity so the badge fits the light report header better.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered ACE/S+/S/A/B/C/D template samples and confirmed only border/background variables are emitted.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - None.

## 2026-05-22 - Equipment Rating Rank-Colored Score Badge

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added an ACE/S+/S/A/B/C/D rank theme palette for the equipment-rating report header.
  - Passed the current rank theme to the template with accent, light, deep, RGB, and readable score color values.
  - Updated the top-right floating score badge border, background, shadow, score text, and subtitle to use the current rank color.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered the equipment-rating template for ACE/S+/S/A/B/C/D sample themes and confirmed CSS variables are emitted.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - D rank uses the deep gray score color instead of the white accent so the score remains readable on a light background.

## 2026-05-22 - Equipment Rating Score Badge Revert

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Reverted the decorative score overlay back to the larger floating score badge card.
  - Kept the prior right-top absolute positioning and enlarged badge sizing.
- Validation:
  - Confirmed the decorative `top-rank::before` and `top-score-copy` styles are absent.
  - Rendered the equipment-rating template with sample header data.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - None.

## 2026-05-22 - Equipment Rating Decorative Score Badge

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed the card-like border, background, radius, and shadow from the floating score badge.
  - Changed the score area into a decorative overlay with a larger rank icon, larger score text, and a subtle gold highlight band behind it.
- Validation:
  - Rendered the equipment-rating template with sample header data and confirmed the old nested-card badge styling is absent.
  - Captured a temporary Playwright preview outside the repository to check the decorative score overlay.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A live screenshot check is useful to confirm the decorative highlight remains subtle with different rank icons.

## 2026-05-22 - Equipment Rating Floating Score Badge

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Changed the top-right equipment-rating score badge to absolute positioning inside the report header.
  - Enlarged the floating badge, rank icon, score text, spacing, padding, radius, and shadow.
  - Reserved header right padding so the title and tags do not overlap the floating score badge.
- Validation:
  - Rendered the equipment-rating template with sample header data and confirmed the score badge uses absolute positioning.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A live screenshot with long header chips is still useful to confirm the reserved right space is sufficient.

## 2026-05-22 - Equipment Rating Header Decoration Cleanup

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed the pale blue circular pseudo-element from the equipment-rating header background because it read as an unintended `O` shape.
- Validation:
  - Confirmed the `.dps-header::before` circular decoration is absent from the template.
  - Rendered the equipment-rating template with sample header data.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - None.

## 2026-05-22 - Equipment Rating Header Copy And Badge Size

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed `配装` from the equipment-rating report header title.
  - Slightly enlarged the top-right score badge, including its icon, score text, spacing, and padding.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered the equipment-rating template with sample header data and confirmed `配装体检报告` is absent.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A live screenshot check is still useful if a very long kungfu name is rendered.

## 2026-05-22 - Equipment Rating Report Header Card

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Reworked the equipment-rating top area into a lightweight horizontal report header card.
  - Changed the title to the current kungfu report title, such as `太虚剑意体检报告`.
  - Rendered suggested optimization slots as pale gold pill tags and moved the loop/buff summary chips into the header.
  - Integrated the grade icon and total score into a subtle gold score badge.
  - Changed the Inkar artwork to a smaller circular avatar crop with a soft blue border/shadow to hide the white square background edge.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered the equipment-rating template with sample header data and confirmed the title, priority tags, and score badge output.
  - Captured a temporary Playwright preview outside the repository to check the report header card layout.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A live render with a long kungfu name is still useful to tune exact title truncation if needed.

## 2026-05-22 - Equipment Rating Floating Header

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed the border and pale background from the equipment-rating top header summary.
  - Changed the local Inkar artwork to an absolutely positioned floating avatar so it does not participate in the text layout.
  - Replaced the header copy with `体检报告` and enlarged the suggested optimization slot text.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered the equipment-rating template with sample header data and confirmed the old summary/score copy is absent.
  - Captured a temporary Playwright preview outside the repository to check the floating header layout.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A live screenshot check with full equipment rows is still useful to tune the floating avatar position if needed.

## 2026-05-22 - Equipment Rating Header Summary

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added the local `Inkar.jpg` equipment-rating artwork as a compact top-header avatar.
  - Reworked the equipment-rating top whitespace into a summary header with total grade text and prioritized optimization slots.
  - Prioritized slots by positive single-piece upgrade value, falling back to the lowest rated slots when no positive upgrade is available.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered the equipment-rating template with sample header data and captured a temporary Playwright preview outside the repository.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check` (only existing CRLF normalization warnings).
- Follow-ups / Risks:
  - A live screenshot check with real role data is still useful to tune exact header spacing if needed.

## 2026-05-22 - Equipment Rating Income Visual Tuning

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed the border and background from the sidebar enchant-income chart.
  - Increased label/value text, column widths, gaps, and bar height slightly for better readability.
- Validation:
  - Ran template text checks confirming the removed border/background styles are gone from `.income-bars`.
- Follow-ups / Risks:
  - A live screenshot check is still useful with real role data to tune spacing if needed.

## 2026-05-22 - Equipment Rating Income Horizontal Bars

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Reworked the sidebar enchant-income chart into a horizontal ranked bar chart.
  - Each row now shows attribute name, a normalized horizontal bar, and a compact signed value.
  - The highest-income row uses a soft cyan accent; other bars use muted blue fills on pale tracks with a subtle midpoint reference.
  - Changed compact large values to one decimal `万` labels such as `+58.6万`.
- Validation:
  - Ran a NoneBot-initialized helper check with the provided sample values, confirming sorted rows and compact labels.
  - Rendered the Jinja template with sample rows and confirmed the chart is in the sidebar and uses the horizontal row structure.
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
- Follow-ups / Risks:
  - A live screenshot check is still useful with real role data to tune exact sidebar spacing if needed.

## 2026-05-22 - Equipment Rating Income Compact Values

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Formatted enchant-income chart values above ten thousand with `万` units.
  - Kept bar ordering and height calculations based on the original numeric values.
- Validation:
  - Ran a NoneBot-initialized helper check confirming `12345` formats as `+1.23万` and smaller values stay as integers.
- Follow-ups / Risks:
  - The running bot process must reload before compact income labels appear.

## 2026-05-22 - Equipment Rating Income Single Row

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Changed the sidebar enchant-income chart from a wrapping grid to a single horizontal row.
  - Kept vertical bars, with smaller bar width and text sizing so all displayed attributes stay in one row.
- Validation:
  - Rendered the Jinja template with six sample income bars and confirmed `.income-bars` appears as a single flex row without grid wrapping.
- Follow-ups / Risks:
  - A live screenshot check is still useful with real long values to confirm the narrow sidebar remains readable.

## 2026-05-22 - Equipment Rating Critical Damage Income

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added critical-damage income to the equipment-rating enchant income chart.
  - Critical-damage now uses the same enchant-equivalent scale as critical, overcome, strain, and surplus: `3279 / 100`.
- Validation:
  - Ran a NoneBot-initialized helper check confirming critical-damage appears as `会效` and scales by `3279 / 100`.
- Follow-ups / Risks:
  - The running bot process must reload before critical-damage appears in the chart.

## 2026-05-22 - Equipment Rating Enchant Income Scale

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Converted the attribute income chart from raw `每100点` DPS gain to enchant-equivalent gain during rendering.
  - Attack income uses `891 / 100`; critical, overcome, strain, and surplus use `3279 / 100`.
  - Attributes without an explicit enchant scale are omitted from the chart to avoid misleading values.
  - Renamed the sidebar chart heading to `附魔收益`.
- Validation:
  - Ran a NoneBot-initialized helper check confirming attack and overcome values are scaled and critical-damage is omitted.
- Follow-ups / Risks:
  - The running bot process must reload before the chart shows enchant-equivalent values.

## 2026-05-22 - Equipment Rating Attribute Income Placement

- Branch: rating
- Type: change
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Moved the attribute income chart from above the equipment list to the sidebar below 配装总评级.
  - Kept the chart as vertical bars and resized it for the narrower sidebar layout.
- Validation:
  - Rendered the Jinja template with sample `attribute_incomes` and confirmed the chart block appears in the sidebar before `</aside>`.
- Follow-ups / Risks:
  - A live screenshot check is still useful after restarting the bot and calculator, because the final vertical height depends on real slot and talent data.

## 2026-05-22 - Equipment Rating Haste Display

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Kept equipment-rating sidebar basic/detail attribute grouping aligned with the attribute export command.
  - Special-cased the `加速` row in equipment-rating rendering to display as `数值 / 段数`, matching the previous rating image style.
  - Did not change the standalone attribute command export output.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran a NoneBot-initialized helper check confirming `加速=9232` renders as `9,232 / 2`.
- Follow-ups / Risks:
  - The running bot process must reload before the equipment-rating image uses the restored haste display.

## 2026-05-22 - Equipment Rating Attribute Income Chart

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Read calculator `summary.attribute_incomes` from equipment-rating responses.
  - Mapped raw `attribute_key` values through the existing attribute-name helper and prepared relative bar heights from `dps_per_100`.
  - Added a compact attribute-income bar chart above the equipment slot list in the exported rating image.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py src\utils\database\attributes.py src\plugins\jx3\attributes\v4.py`.
  - Ran a NoneBot-initialized helper check confirming raw income keys render as short labels and normalized percentages.
  - Rendered the Jinja template with sample `attribute_incomes` and confirmed the chart block is present.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload after calculator is restarted with `summary.attribute_incomes`.

## 2026-05-22 - Equipment Rating Attribute Sections

- Branch: rating
- Type: change
- Files changed:
  - src/utils/database/attributes.py
  - src/plugins/jx3/attributes/v4.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Extracted the attribute-command basic/detail attribute split into shared `split_display_attributes()`.
  - Updated the attribute v4 export path to use the shared helper without changing its displayed grouping.
  - Passed the current `JX3PlayerAttribute` object into equipment-rating rendering so its sidebar basic/detail attributes come from the same `JX3PlayerAttribute.attributes` display data as the 属性 command.
  - Kept calculator `summary.attributes` as a fallback when a render call has no local equipment object.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\utils\database\attributes.py src\plugins\jx3\attributes\v4.py src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran a NoneBot-initialized helper check confirming equipment-rating `_prepare_attributes()` and `split_display_attributes()` return the same DPS basic/detail grouping.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before equipment-rating images use the shared attribute sections.

## 2026-05-22 - Equipment Rating Raw Attribute Keys

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Allowed equipment-rating item attributes to consume raw calculator attribute keys.
  - Kept using the shared attribute-query `get_attr_name()` helper for display text.
  - Still hides unknown raw `at*` fields, defensive fields, invalid fields, skill-event handlers, and set recipe triggers from the exported image.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran a NoneBot-initialized helper check confirming raw keys render as `攻击 会心 破防 会效 无双` while unknown/special raw keys are hidden.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before exported images consume raw calculator attribute keys.

## 2026-05-22 - Equipment Rating Attribute Short Names

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Reused the attribute command's `get_attr_name()` helper when formatting equipment-rating item attributes.
  - Removed the local long-name compatibility mapping; unknown or already formatted labels are kept as-is.
  - Applied the same formatting path to current equipment attributes and best-candidate attribute summaries.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before exported images use abbreviated attribute labels.

## 2026-05-22 - Equipment Rating Best Attributes

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added best-candidate level and attribute summary to the equipment rating image best-note text.
  - The best note now formats the candidate like `最优 装备名（41400 外功攻击 外功会心 ...）: +提升`.
  - Reused calculator-provided `best.attribute` and existing hidden-attribute filtering.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before export images include best-candidate attributes.

## 2026-05-21 - Equipment Rating Support Current Season First

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Sorted `装备评级支持` season groups so the calculator `current_season` group is displayed first.
  - Kept non-current season groups ordered by the smallest internal kungfu ID in each group.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before the season order changes.

## 2026-05-21 - Equipment Rating Support Merge Same School

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Merged same-school kungfus under each season group into one line, e.g. `少林：洗髓经、易筋经`.
  - Sorted school rows by the smallest internal kungfu ID in that row, and sorted names inside each row by kungfu ID.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before the merged list format appears.

## 2026-05-21 - Equipment Rating Support Group By Season

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed `装备评级支持` list output to group kungfus under `【赛季】` headings.
  - Kept each season group sorted by internal kungfu ID while hiding the numeric IDs.
  - Rendered group rows as `门派：心法`.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before the grouped list format appears.

## 2026-05-21 - Equipment Rating Support Sort By Kungfu ID

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed `装备评级支持` list output from school grouping to one kungfu per line.
  - Sorted the visible list by internal kungfu ID in ascending order without displaying the numeric ID.
  - Kept season labels as `【赛季】`.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before the list order changes.

## 2026-05-21 - Equipment Rating Support Season Brackets

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed `装备评级支持` season labels from square brackets with status text to Chinese brackets around the season only.
  - Removed `当前` / `可能过时` status wording from list and detail replies while keeping calculator metadata unchanged.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall -q bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload before the reply format changes.

## 2026-05-21 - Equipment Rating Support Hide Kungfu IDs

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Removed numeric kungfu IDs from user-facing `装备评级支持` list and detail replies.
  - Updated the support usage prompt to show `<心法名>` only while keeping internal ID matching compatible.
  - Removed numeric ID fallback from unsupported-kungfu and rating-image kungfu-name display.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Searched the equipment rating support handler for remaining visible `心法ID` / kungfu-id formatting.
- Follow-ups / Risks:
  - The running bot process must reload before replies stop showing numeric IDs.

## 2026-05-21 - Equipment Rating JCL Record Labels

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Read calculator `selected.jcl_record` metadata from `/equipment_rating/kungfus`.
  - Added compact JCL record status labels to `装备评级支持`.
  - Added single-kungfu detail lines for JCL season, record time, current season, and notes.
  - Kept compatibility with older calculator responses by showing `未标注` when metadata is absent.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py src\plugins\jx3\calculator\__init__.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload to show these labels.
  - Unconfigured calculator records intentionally show `未标注`.

## 2026-05-21 - Equipment Rating Progress Prompt

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added an immediate `装备评级中，请稍后。` message before the bot enters the slow equipment lookup and calculator request path.
  - The default equipment rating command sends the prompt after basic server/kungfu validation.
  - The public-JCL list flow sends the prompt after the user selects a loop number, before loading role equipment and calling `/equipment_rating`.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process is currently stopped by request; restart it manually to load this behavior.

## 2026-05-21 - Equipment Rating Public JCL List

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Replaced the user-facing direct `JCL序号` parameter with `装备评级 <服务器> <角色> <心法> 评级列表`.
  - The list mode fetches calculator `/loops` and prompts the user with the same public JCL order as the normal calculator command.
  - After the user replies with a loop number, the bot passes the corresponding internal `jcl_index` to calculator; no fourth argument still uses the default `rating_jcl` path.
  - Moved role/equipment lookup out of the initial list step, so `评级列表` returns the loop list before the slower 推栏装备读取 and only loads equipment after the user selects a loop.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Requires the bot process to reload so the new `got("rating_jcl_order")` handler is registered.
  - The calculator still needs the existing `jcl_index` support for the selected public JCL call.

## 2026-05-21 - Equipment Rating Matcher And JCL Index

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Moved equipment rating matcher declarations into the calculator plugin `__init__.py`.
  - Left equipment rating rendering and handler implementation in `equipment_rating.py`.
  - Added optional command parameter `JCL序号` for `装备评级 <服务器> <角色> <心法> [JCL序号]`.
  - Omitted `JCL序号` continues to use calculator `rating_jcl`; a positive index asks calculator to use `jcl/<心法ID>/` with the same index semantics as the calculator loop list.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Requires a calculator version that accepts the new `jcl_index` request field.

## 2026-05-21 - Equipment Rating DPS Hidden After Debug

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Hid the temporary rating DPS display after confirming the DPS change came from upstream calculator data.
  - Kept the equipment rating image using calculator-provided decoration chips.
  - Kept the render guard that drops generic `五行石X级` fallback chips.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
  - Confirmed `current_dps_text` / `top-dps` / `评级DPS` no longer appear in equipment rating render code.
- Follow-ups / Risks:
  - Running bot process needs reload before the export image stops showing rating DPS.

## 2026-05-21 - Equipment Rating DPS Debug And Calculator Decorations

- Branch: rating
- Type: change
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Restored visible rating DPS in the equipment rating export image for the current debugging pass.
  - Added `summary.current_dps_text` to render data and displayed it in the top header and total rating panel.
  - Kept equipment rating decoration chips sourced from calculator response fields only.
  - Removed the bot-side submitted-equipment decoration fallback after settling on the calculator response as the single source of truth.
  - Dropped generic calculator fallback chips like `五行石8级` from rendering, so only decoration text with real attribute/name content reaches the image.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - This intentionally re-enables a value that was previously hidden; remove it again after score-difference investigation if needed.
  - Running bot and calculator processes both need reloads before calculator-sourced decoration labels reflect the latest behavior.

## 2026-05-21 - Equipment Rating Upstream Merge

- Branch: rating
- Type: integration
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Committed and pushed the per-slot best-equipment gain restore.
  - Merged `upstream/main` into `rating` without conflicts and pushed the merge result to `origin/rating`.
- Validation:
  - Before commit, ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Before commit, ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Before commit, ran `git diff --check`.
- Follow-ups / Risks:
  - Calculator needed a manual conflict resolution for the upstream `rating_jcl` rename; the bot merge itself did not require conflict edits.

## 2026-05-21 - Equipment Rating Slot Gain Restore

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Restored the per-slot best-equipment gain text in the equipment rating export image.
  - Kept the top-level rating DPS hidden; only the single-item improvement delta is shown again.
  - Confirmed this uses existing calculator fields (`best.dps` and `rating.current_dps`) and does not require a response contract change.
- Validation:
  - Pending final syntax and diff checks in this turn.
- Follow-ups / Risks:
  - Running bot process must reload before rendered images show the restored per-slot gain.

## 2026-05-21 - Equipment Rating Decoration Fallback Rollback

- Branch: rating
- Type: rollback
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Rolled the PR branch back to `9942378a`, the post-upstream-rebase state before the later decoration fallback amendment.
  - Removed the bot-side local decoration fallback from the submitted PR branch.
- Validation:
  - Confirmed `9942378a` contains `upstream/main`.
  - Ran `git reset --hard 9942378a`.
  - Ran `git push --force-with-lease origin rating`.
- Follow-ups / Risks:
  - The PR now has the same equipment rating render behavior it had when first created after the upstream rebase.

## 2026-05-21 - Equipment Rating Decoration Fallback

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added a bot-side fallback that fills equipment rating decoration chips from the local submitted equipment record when the calculator API response omits embedding, enchant, and color-stone display fields.
  - Kept API-provided decoration fields as the first choice so richer calculator responses still render unchanged.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
  - Verified against local `二二洛白二二` equipment data that chips are filled even when `/equipment_rating` returns no decoration fields.
- Follow-ups / Risks:
  - Live OneBot/NapCat image send was not retried in this turn.

## 2026-05-21 - Equipment Rating Upstream Rebase

- Branch: rating
- Type: integration
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - src/utils/database/attributes.py
  - worklog.md
- Summary:
  - Rebasing `rating` onto latest `upstream/main` kept the independent `equipment_rating.py` command module and `equipment_rating.html` template instead of adopting the upstream deletion.
  - Restored the calculator package import so the independent `装备评级` command still registers.
  - Preserved the equipment-rating render image updates and attribute submit/JCL validation behavior from the branch.
- Validation:
  - `pdm run python -m compileall bot.py config.py src` could not run because `pdm` is not available in the current PATH.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Live OneBot/NapCat image sending and remote calculator API behavior were not exercised locally.

## 2026-05-21 - Equipment Rating Output Cleanup

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Disabled the local post-rating JSON response log and removed the `logs/equipment_rating.log` write path.
  - Kept runtime logging only for image-send failure handling.
  - Temporarily hid equipment rating DPS from the export image, including the best-candidate DPS delta text.
  - Improved the support-heart-method query failure text when calculator is still running an old process without `/equipment_rating/kungfus`.
- Validation:
  - Confirmed no remaining `equipment_rating.log`, JSON dump helper, or `Time` usage in the equipment rating plugin.
  - Full compile and diff checks are pending in the final pre-commit verification pass.
- Follow-ups / Risks:
  - The running bot must restart or hot reload to remove the local log behavior.

## 2026-05-20 - Equipment Rating Hide DPS

- Branch: rating
- Type: fix
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Temporarily hid the top-level `评级DPS` label and value from the equipment rating export image.
  - Kept the total rating icon and score visible, and did not change calculator response data or scoring logic.
- Validation:
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload to pick up template changes; `dev_reload.py` ignores `src/templates`, so a bot restart may be needed.

## 2026-05-20 - Equipment Rating Send Failure Guard

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Reverted the equipment rating local-file image send trial after a live retry still failed with `rich media transfer failed`.
  - Added an `ActionFailed` guard around the final equipment rating image send.
  - If QQ/NapCat rejects the generated image, the command now attempts a Chinese text fallback instead of surfacing as a bot code error.
- Validation:
  - Live retry reported by user: `装备评级 双梦 二二洛白二二 莫问` still failed with `rich media transfer failed` while using local file URI.
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The root cause appears to be in the QQ/NapCat rich media upload path or a QQ-side image acceptance rule, not database retrieval or local image generation.

## 2026-05-20 - Equipment Rating Local File Send Trial

- Branch: rating
- Type: diagnostic
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Changed the equipment rating image send path to keep the rendered PNG on disk and send it via a local `file:///...` URI.
  - Scoped the trial to the `装备评级` command so it can distinguish local-file rich media upload from the existing base64 image path.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Confirmed `MessageSegment.image(Path(...).as_uri())` serializes the image file as a `file:///C:/...` URI instead of `base64://...`.
- Follow-ups / Risks:
  - Needs a live `装备评级 双梦 二二洛白二二 莫问` retry through NapCat to confirm whether local file upload avoids `rich media transfer failed`.

## 2026-05-20 - Image Send JPG Fallback Rollback

- Branch: rating
- Type: rollback
- Files changed:
  - src/utils/message.py
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Rolled back the temporary JPG image-send fallback trial.
  - Restored `src/utils/message.py` to its original message hook helpers only.
  - Restored attribute image handling to the previous text-only `ActionFailed` fallback.
  - Restored equipment rating image sending to the existing direct image finish path.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\utils\message.py src\plugins\jx3\attributes\__init__.py src\plugins\jx3\calculator\equipment_rating.py` after rollback.
  - Ran `git diff --check` after rollback.
- Follow-ups / Risks:
  - The underlying NapCat/QQNT rich media upload failure still needs protocol/runtime-level diagnosis.

## 2026-05-20 - Attribute Cache Cleanup

- Branch: rating
- Type: data fix
- Files changed:
  - src/data/attributes.db (ignored runtime data)
  - worklog.md
- Summary:
  - Deleted the local `player_equip` cache row for `二二洛白二二` (`global_role_id=8330138861394596027`, previous `player_equip.id=4024`).
  - Kept the role lookup/binding data untouched.
- Validation:
  - Confirmed one matching `player_equip` row existed before deletion.
  - Ran a targeted SQLite delete and removed 1 row.
  - Rechecked `player_equip` for `global_role_id=8330138861394596027`; no matching rows remain.
- Follow-ups / Risks:
  - A future upload can recreate this cache entry unless submit/input validation rejects or normalizes the incoming payload.

## 2026-05-20 - Attribute Send Failure Guard

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - worklog.md
- Summary:
  - Added a guarded finish helper for attribute query responses.
  - If QQ/NapCat rejects the generated attribute image with `ActionFailed`, the matcher now attempts a text fallback instead of surfacing as a bot code error.
  - If even the fallback text send fails, the send error is logged and swallowed so the matcher does not poison the global error path.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\attributes\__init__.py src\utils\database\attributes.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - This prevents the attribute command from making the bot look broken, but does not fix the underlying QQ/NapCat rich media upload failure.

## 2026-05-20 - Attribute Local File Send Rollback

- Branch: rating
- Type: rollback
- Files changed:
  - src/plugins/jx3/attributes/v2_remake.py
  - src/plugins/jx3/attributes/v4.py
  - worklog.md
- Summary:
  - Reverted the attribute image local-file send experiment.
  - Restored v2r and v4 attribute image sending to the original `MessageSegment.image(bytes)` / base64 path.
- Validation:
  - Ran `git restore --worktree -- src\plugins\jx3\attributes\v2_remake.py src\plugins\jx3\attributes\v4.py`.
- Follow-ups / Risks:
  - The QQ/NapCat `rich media transfer failed` issue remains unresolved and should be diagnosed at the protocol/runtime layer or with controlled image-send tests.

## 2026-05-20 - Attribute Local File Image Send Trial

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/attributes/v2_remake.py
  - src/plugins/jx3/attributes/v4.py
  - worklog.md
- Summary:
  - Changed v2r and v4 attribute image messages to pass generated local cache file paths to OneBot instead of large base64 payloads.
  - Switched from `file:///C:/...` URI output to plain `C:/.../src/cache/*.png` paths to match NapCat local-path resource handling.
  - Confirmed `属性 简单 倦收天` generates valid local PNG data and now returns CQ image messages with plain local file paths.
  - Checked NapCat OneBot status: online/good and `can_send_image` reports true, so the remaining test is whether QQ/NapCat accepts local-file image upload in the live group.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\attributes\v2_remake.py src\plugins\jx3\attributes\v4.py src\plugins\jx3\attributes\__init__.py src\utils\database\attributes.py`.
  - Ran a local smoke query for `属性 简单 倦收天`; v4 and v2r returned `file=C:/Users/.../src/cache/*.png` CQ image segments.
- Follow-ups / Risks:
  - If local-file image upload still fails in the live group, the failure is likely QQNT/NapCat runtime upload state rather than payload transport size.

## 2026-05-20 - Attribute Upload Bad Data Guard

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - src/utils/database/attributes.py
  - src/data/attributes.db (ignored runtime data)
  - worklog.md
- Summary:
  - Deleted the bad local equipment cache for `双梦 二二洛白二二 莫问` (`player_equip.id=4021`).
  - Added render-path validation before saving submitted attribute data so unusable equipment exports are rejected instead of corrupting the local cache.
  - Changed group `.jcl` uploads to save each parsed role independently, skip unusable role data, and report skipped entries without breaking the whole upload.
  - Hardened JCL parsing so malformed equipment/talent rows are filtered before cache instances are built.
  - Filtered unusable historical cache records during attribute lookup so one bad record cannot break the full attribute query.
- Validation:
  - Confirmed the target `二二洛白二二` / 莫问 cache entry was removed and no matching `global_role_id=8330138861394596027`, `kungfu_id=10447` record remains.
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\attributes\__init__.py src\utils\database\attributes.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran helper checks after `nonebot.init()` confirming an empty attribute instance is rejected and a known good cache record still validates.
  - Inserted a temporary empty attribute cache record and confirmed `JX3PlayerAttribute.from_database(..., all=True)` skips it and returns `None`; the temporary record was deleted.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Ignored runtime DB deletion affects only this local workspace.

## 2026-05-20 - Equipment Rating Support Command

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added `装备评级支持`, `装备评级心法`, and `装备评级支持心法` command aliases.
  - The command lists supported equipment-rating kungfus grouped by school, or checks a specific kungfu by name or ID and reports the default rating loop.
  - The command reads support data from calculator `GET /equipment_rating/kungfus` so the list follows the current `ratingJcl` directory.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran helper formatting checks after `nonebot.init()`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload to register the new command.
  - The calculator service must reload first so `/equipment_rating/kungfus` exists.

## 2026-05-20 - Equipment Rating Hide Effects

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Removed equipment rating effect text preparation and the orange effect line from the export template.
  - Kept renderer-side filtering for raw `at*` tokens so skill-event, set-recipe, and weapon damage fields remain hidden if an older calculator response still contains them.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `rg` checks confirming no `effect_text` / `item-effect` render path remains.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - The running bot process must reload to pick up template changes; `dev_reload.py` ignores `src/templates`, so a bot restart may be needed.
  - `src/templates/jx3/equipment_rating.html` already had staged user changes before this work; this entry only describes the additional unstaged renderer changes.

## 2026-05-20 - Equipment Rating Effects

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added renderer support for calculator-provided equipment `effects` and displays them as a compact orange text line under the current item's decoration chips.
  - Hardened attribute text rendering so old calculator responses containing raw `at*` tokens such as weapon damage fields, `atSkillEventHandler`, or `atSetEquipmentRecipe` do not leak into the exported rating image.
  - Kept the best candidate visually condensed; effect text is rendered only for current equipment rows.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran a direct helper check after `nonebot.init()` confirming raw `at*` tokens are filtered and duplicate effect texts are deduplicated.
  - Rendered a fixed sample report through `render_equipment_rating_image()` after `ScreenshotGenerator.launch()`; output completed successfully.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Live command output depends on a restarted calculator service that returns the new `effects` field.
  - `src/templates/jx3/equipment_rating.html` already had staged user changes before this work; this entry only describes the additional unstaged renderer changes.

## 2026-05-20 - Equipment Rating Attribute Filter

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Added renderer-side filtering for equipment rating attribute text so defense, invalid, skill-event, set-recipe, and vitality display fields are omitted from exported rating images.
  - Kept the main ordering contract on the calculator side while making the renderer tolerant of older calculator responses that may still include raw hidden field names, including values with stray whitespace.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - This only changes display filtering; scoring and calculator inputs are unaffected.

## 2026-05-20 - Equipment Rating Decorations

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added renderer preparation for calculator-provided equipment embedding, color stone, and enchant metadata.
  - Rendered current-equipment decorations as compact icon + text chips under the item attributes, using local five-stone and enchant assets plus calculator color-stone icon URLs when available.
  - Preserved the existing raw-response debug log path and prior talent/footer template changes.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Rendered a fixed sample report through `render_equipment_rating_image()` after initializing NoneBot and Playwright; output completed successfully.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Live bot command verification still depends on a restarted calculator service that includes the new `/equipment_rating` response fields.

## 2026-05-20 - Equipment Rating Raw Response Log

- Branch: rating
- Type: chore
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - worklog.md
- Summary:
  - Restored the dedicated `logs/equipment_rating.log` debug path for equipment rating.
  - Each successful `/equipment_rating` response parse appends timestamp, server, role, kungfu, and the complete formatted JSON response.
  - Kept the earlier table-format experiment removed; the log now records raw returned data for debugging.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - `logs/equipment_rating.log` is ignored by Git via `*.log` and is created on the next equipment rating call.

## 2026-05-20 - Equipment Rating Talent Layout

- Branch: rating
- Type: fix
- Files changed:
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Changed the equipment rating talent strip from a fixed 10-column grid to an auto-fitting grid so talent icons tile evenly based on available width.
- Validation:
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Visual verification with live rating data was not run; layout change is limited to CSS.

## 2026-05-20 - Equipment Rating And Local Debug Tools

- Branch: rating
- Type: feature
- Files changed:
  - bot.py
  - dev_reload.py
  - docker-compose.dev.yml
  - src/assets/image/jx3/equipment_rating/rank_a.png
  - src/assets/image/jx3/equipment_rating/rank_ace.png
  - src/assets/image/jx3/equipment_rating/rank_b.png
  - src/assets/image/jx3/equipment_rating/rank_c.png
  - src/assets/image/jx3/equipment_rating/rank_d.png
  - src/assets/image/jx3/equipment_rating/rank_s.png
  - src/assets/image/jx3/equipment_rating/rank_s_plus.png
  - src/assets/source/config.yml
  - src/config/__init__.py
  - src/const/jx3/kungfu.py
  - src/const/prompts.py
  - src/plugins/jx3/attributes/__init__.py
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/plugins/jx3/equip/equip_find.py
  - src/plugins/jx3/joy/random_equip.py
  - src/plugins/jx3/skill/martix.py
  - src/plugins/private_commands/__init__.py
  - src/templates/jx3/equipment_rating.html
  - src/utils/network.py
  - worklog.md
- Summary:
  - Added the `装备评级` command, rating report renderer, HTML template, and rank image assets for calculator-service equipment rating results.
  - Expanded `提交属性` so 茗伊 export data can be supplied inline, local role records can be created when API lookup is missing, and follow-up imports save the role index.
  - Added optional local debugging support through a hot-reload script, development compose file, private-command proxy configuration, and localhost proxy bypass in HTTP requests.
  - Hardened related JX3 flows for missing equipment search results, optional set attributes, matrix API response gaps, and the 山居问水诀 kungfu conversion.
- Validation:
  - `pdm run python -m compileall bot.py config.py src` could not run because `pdm` is not available in the current PATH.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Live bot verification still requires local OneBot adapter/config and a reachable calculator service implementing `/equipment_rating`.

## Entry Template

```markdown
## YYYY-MM-DD - Short Title

- Branch: branch-name
- Type: docs | feature | fix | refactor | test | chore | dependency | asset | workflow
- Files changed:
  - path/to/file
- Summary:
  - What changed and why.
- Validation:
  - Commands run, manual checks performed, or why validation was skipped.
- Follow-ups / Risks:
  - Remaining work, assumptions, or known risk.
```

## 2026-05-19 - Attribute Submit Local Role Records

- Branch: rating
- Type: feature
- Files changed:
  - src/const/prompts.py
  - src/plugins/jx3/attributes/__init__.py
  - worklog.md
- Summary:
  - Rolled back the generic `UID` to `角色ID` prompt wording change.
  - Changed `提交属性` so a missing role record no longer blocks local import; it now generates a deterministic local global role ID from `服务器:角色` and saves both the local role index and the submitted equipment data.
  - Kept the existing role-ID lookup path when it succeeds, but no longer requires a prior `提交角色` or JX3API lookup for role-name-only local imports.
- Validation:
  - Ran `python -m compileall src\const\prompts.py src\plugins\jx3\attributes\__init__.py`.
  - Used `.venv\Scripts\python.exe` to verify `姨妈` resolves to `斗转星移`, `剑纯` resolves to `太虚剑意`, `疏于` gets a deterministic local ID, and the provided 茗伊 export string parses into equipment data.
  - Built a `JX3PlayerAttribute` instance from the provided export string with the generated local ID without saving to runtime data.
- Follow-ups / Risks:
  - Synthetic local IDs are only for this bot's local databases. Running `提交角色` later with real API data will replace the local role index for the same角色名 and服务器.

## 2026-05-19 - Equipment Rating Canvas Margin

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Added an outer `.rating-canvas` wrapper for the equipment rating report and changed screenshot capture to target the wrapper instead of the content block.
  - Kept the report content width the same while moving whitespace to the captured canvas, avoiding the cropped-edge look in the exported image.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Rendered a fixed sample report with Playwright and visually checked `src/cache/equipment_rating_reference_test.png`.
  - Ran `git diff --check -- src\plugins\jx3\calculator\equipment_rating.py src\templates\jx3\equipment_rating.html`.
- Follow-ups / Risks:
  - Live command verification still requires the running bot adapter and calculator service.

## 2026-05-19 - Equipment Rating Reference Report

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - worklog.md
- Summary:
  - Reworked the equipment rating renderer toward the reference vertical white report: left sidebar for role/basic/detail attributes and total rank, right panel for rating DPS, chips, and 12 ordered equipment rows.
  - Added renderer-side preparation for equipment icons, quality colors, reference slot order, percentage attributes, haste segment display, best-candidate DPS delta, and talent icons from calculator `summary.talents`.
  - The template now captures internal white margins so the exported image matches the reference report proportions instead of cropping content against the image edge.
- Validation:
  - Ran `.venv\Scripts\python.exe -m py_compile src\plugins\jx3\calculator\equipment_rating.py`.
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Rendered a fixed sample report with Playwright and visually checked `src/cache/equipment_rating_reference_test.png`.
  - Ran `git diff --check -- src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\equipment_rating.py src\templates\jx3\equipment_rating.html src\assets\image\jx3\equipment_rating`.
- Follow-ups / Risks:
  - Live bot command verification was not run because it requires a running OneBot adapter and calculator service with the new route loaded.
  - Actual equipment icons and talent icons are loaded from JX3Box icon URLs during rendering, so image generation depends on those remote assets being reachable.

## 2026-05-19 - Equipment Rating Command

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - src/plugins/jx3/calculator/equipment_rating.py
  - src/templates/jx3/equipment_rating.html
  - src/assets/image/jx3/equipment_rating/rank_a.png
  - src/assets/image/jx3/equipment_rating/rank_ace.png
  - src/assets/image/jx3/equipment_rating/rank_b.png
  - src/assets/image/jx3/equipment_rating/rank_c.png
  - src/assets/image/jx3/equipment_rating/rank_d.png
  - src/assets/image/jx3/equipment_rating/rank_s.png
  - src/assets/image/jx3/equipment_rating/rank_s_plus.png
  - worklog.md
- Summary:
  - Added `装备评级 <服务器> <角色> <心法>` as a one-shot command with no loop or buff selection.
  - The command reuses the existing role lookup and 推栏装备缓存 flow, sends `kungfu_id` / `jcl_data` / role metadata / fixed `32500-43000` candidate level range to calculator `/equipment_rating`, and renders the returned JSON into a vertical white report image.
  - Added equipment rating rank icons copied from the reference project and a dedicated report template showing total rating, DPS, fixed loop, default rating buffs, formation, per-slot score, current equipment, best candidate, candidate count, and haste conversion.
- Validation:
  - Ran `.venv\Scripts\python.exe -m compileall bot.py config.py src`.
  - Rendered a fixed sample JSON through `src/templates/jx3/equipment_rating.html` with Playwright; output image `src/cache/5742d2df538111f19422acf23c25b344.png` was visually checked.
  - Ran `git diff --check -- src\plugins\jx3\calculator\__init__.py src\plugins\jx3\calculator\equipment_rating.py src\templates\jx3\equipment_rating.html src\assets\image\jx3\equipment_rating`.
- Follow-ups / Risks:
  - Live bot command verification was not run because it requires the running OneBot adapter and a live calculator service with the new route loaded.
  - First full 10015 sample calculation on calculator took about 126 seconds, so the bot request timeout is set to 300 seconds; persistent cache or progress feedback may be needed if more心法 or larger候选池 are added.

## 2026-05-19 - Matrix Empty Description Handling

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/skill/martix.py
  - worklog.md
- Summary:
  - Added defensive handling for missing or empty 推栏阵眼 data so `阵眼 剑纯` no longer crashes when `zhenFa.descs` is `null`.
  - Added fallback responses when the matched心法 has no阵眼描述 or no matching阵眼 data is returned.
- Validation:
  - Ran `python -m compileall src\plugins\jx3\skill\martix.py`.
  - Ran a standalone fake-response script for `阵眼 剑纯` with `descs: None` and confirmed it returns a Chinese fallback message instead of raising `TypeError`.
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - Live 推栏 validation was not run because the local Python environment is missing project dependencies such as NoneBot/PyYAML outside the bot runtime.

## 2026-05-19 - Optional Equipment Set Attributes

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/equip/equip_find.py
  - src/plugins/jx3/joy/random_equip.py
  - worklog.md
- Summary:
  - Treated `SetAttributes` as an optional field when rendering equipment cards.
  - Fixed `装备 镇恶` crashing with `KeyError: 'SetAttributes'` because orange weapons returned by the local calculator API do not include that field.
  - Applied the same optional-field handling to the random equipment renderer, which shares the same equipment-card parsing pattern.
- Validation:
  - Ran `python -m compileall src/plugins/jx3/equip/equip_find.py src/plugins/jx3/joy/random_equip.py`.
  - Initialized NoneBot in a standalone script and verified `get_equip_info("镇恶")` returns 6 candidates without raising `KeyError`.
  - Confirmed the running bot hot-reloaded after the changed files.
- Follow-ups / Risks:
  - Missing set data now renders as no set bonus section. If orange weapon recipe effects need explicit display, add parsing for `atSetEquipmentRecipe` separately.

## 2026-05-19 - Equip Compare Empty Search Handling

- Branch: rating
- Type: fix
- Files changed:
  - src/plugins/jx3/calculator/__init__.py
  - worklog.md
- Summary:
  - Added an explicit empty-result response for `装备对比` so a failed equipment search no longer sends only `请从下面选择装备进行对比！` and waits for a choice that does not exist.
  - Reordered equipment index validation to check bounds before indexing the result list.
- Validation:
  - Ran `python -m compileall src/plugins/jx3/calculator/__init__.py`.
- Follow-ups / Risks:
  - The equipment search still depends on the calculator service's `/equip` endpoint and the exact/fuzzy equipment name supplied by the user.

## 2026-05-19 - Localhost Request Proxy Bypass

- Branch: rating
- Type: fix
- Files changed:
  - src/utils/network.py
  - worklog.md
- Summary:
  - Updated the shared `Request` helper so calls to `127.0.0.1`, `localhost`, `0.0.0.0`, and `::1` ignore environment proxy settings.
  - Fixed local calculator requests being routed through `HTTP_PROXY=http://127.0.0.1:10080`, which returned `502 Bad Gateway` and surfaced as `JSONDecodeError` in commands such as `JC计算器 倦收天`.
- Validation:
  - Ran `python -m compileall src/utils/network.py`.
  - Verified `Request("http://127.0.0.1:11223/loops?kungfu_id=10015&user_id=0").get()` returns HTTP 200 JSON.
  - Confirmed the running bot hot-reloaded and later calculator logs reached `/calculator_raw` successfully.
- Follow-ups / Risks:
  - External URLs still trust environment proxy settings; only local hostnames are bypassed.

## 2026-05-19 - Private Command Debug Proxy

- Branch: rating
- Type: feature
- Files changed:
  - src/config/__init__.py
  - src/assets/source/config.yml
  - src/config/config.yml
  - src/plugins/private_commands/__init__.py
  - worklog.md
- Summary:
  - Added `bot_basic.allow_private_commands` and `bot_basic.private_command_group_id` for development-time private chat command debugging.
  - Added a private message proxy plugin that re-dispatches private messages as group-compatible events using the configured group context, allowing existing `GroupMessageEvent` command handlers to run without broad signature rewrites.
  - Redirected normal replies and same-context `send_group_msg` replies back to the private chat while the proxy is active.
  - Enabled the local runtime switch with group context `821696720`.
- Validation:
  - Ran `python -m compileall src/config src/plugins/private_commands`.
  - Verified hot reload loaded `src.plugins.private_commands`.
  - Confirmed private messages are logged once as the original private event and once as the proxied group-context event.
  - Confirmed private `JC计算器 倦收天` reached the calculator command flow and generated output after selecting a loop.
- Follow-ups / Risks:
  - This is intended for local debugging. Commands that directly perform group administration actions may still use the configured group context.

## 2026-05-19 - Development Hot Reload Wrapper

- Branch: rating
- Type: workflow
- Files changed:
  - bot.py
  - dev_reload.py
  - docker-compose.dev.yml
  - worklog.md
- Summary:
  - Added a local development watcher that restarts `python bot.py` when source/config files change, avoiding duplicate plugin loading issues from direct NoneBot/Uvicorn reload attempts.
  - Added a development Docker Compose override that runs the watcher and mounts source/config/data/cache paths for iterative debugging.
  - Normalized the missing trailing newline in `bot.py`.
- Validation:
  - Started the watcher and confirmed it restarts the bot on source/config changes.
  - Verified the bot is listening on `0.0.0.0:2333` after watcher restarts.
  - Confirmed hot reload picked up later edits to config, private command plugin, and network helper.
- Follow-ups / Risks:
  - The watcher filters source-like files only and excludes cache/data/template churn; add extensions if future development needs broader reload coverage.

## 2026-05-19 - Attribute Submit Inline Export Command

- Branch: rating
- Type: feature
- Files changed:
  - src/plugins/jx3/attributes/__init__.py
  - src/const/prompts.py
  - src/const/jx3/kungfu.py
  - worklog.md
- Summary:
  - Added inline `提交属性 <服务器> <角色名/ID> <心法> <茗伊装备导出码>` support so the old two-step submit flow can be completed in one command.
  - Added `提交属性 help` with accepted formats, while keeping the existing two-step command flow.
  - Added role ID lookup fallback through `get_uid_data` for submit flows that provide an ID.
  - Updated missing-equipment prompt to point users at the inline export-code command.
  - Fixed the mobile-to-PC kungfu mapping for `山居问水剑·悟` to resolve to `问水诀`.
- Validation:
  - Ran compile checks during the private command/config validation pass.
  - Verified the bot hot-reloaded after the attribute command changes.
  - Confirmed `提交属性 help` can be sent through the private debug proxy.
- Follow-ups / Risks:
  - Full import success still depends on valid 茗伊 export data and role global ID availability.

## 2026-05-19 - Remove Login Module Draft

- Branch: rating
- Type: chore
- Files changed:
  - docs/mobile-app-equipment-login.md
  - tools/jx3_login_protocol_probe.py
  - worklog.md
- Summary:
  - Removed the draft login-module requirements document and protocol probe script at the user's request.
  - Removed the previous worklog details for that draft and kept this replacement entry to document the cleanup.
- Validation:
  - Ran `git diff --check`.
- Follow-ups / Risks:
  - None.

## 2026-05-19 - Localhost Calculator URL

- Branch: rating
- Type: chore
- Files changed:
  - src/config/config.yml
  - worklog.md
- Summary:
  - Changed the local runtime calculator API URL from `http://10.0.15.4:11223` to `http://127.0.0.1:11223` so the bot uses the parser running on the same Windows host.
  - Restarted the local bot process to reload `src/config/config.yml`.
- Validation:
  - Verified `src.config.Config.jx3.api.calculator_url` reads back as `http://127.0.0.1:11223`.
  - Verified `curl --noproxy` against `http://127.0.0.1:11223/docs` returns HTTP 200.
  - Restarted the bot and verified it is listening on `0.0.0.0:2333`.
  - Verified the restarted bot is connected to NapCat on `127.0.0.1:3001` with an established WebSocket connection.
  - Verified a bot-environment `httpx` request to `/skill` through the configured URL returns HTTP 200 JSON.
- Follow-ups / Risks:
  - `127.0.0.1` only works while the bot and parser run on the same host environment; Docker or another machine should use the host LAN address instead.

## 2026-05-19 - Persistent User NO_PROXY

- Branch: rating
- Type: chore
- Files changed:
  - worklog.md
- Summary:
  - Set Windows user environment variables `NO_PROXY` and `no_proxy` to `10.0.15.4,127.0.0.1,localhost` so new shells can bypass the local HTTP proxy for calculator and local services.
  - Restarted the local bot with the same `NO_PROXY` value in the current process environment.
- Validation:
  - Confirmed user-level `NO_PROXY` and `no_proxy` values were written.
  - Verified the restarted bot is connected to NapCat on `127.0.0.1:3001` with an established WebSocket connection.
  - Confirmed `git status --short --branch` remains clean.
- Follow-ups / Risks:
  - Already-running parent processes do not automatically inherit new Windows user environment values; start future bot sessions from a newly opened terminal, or set `$env:NO_PROXY` in that shell before starting.

## 2026-05-19 - Local Proxy Bypass For Calculator API

- Branch: rating
- Type: chore
- Files changed:
  - worklog.md
- Summary:
  - Diagnosed calculator API failures as proxy-related: requests to `10.0.15.4:11223` returned `502 Bad Gateway` through `HTTP_PROXY=http://127.0.0.1:10080`.
  - Restarted the local bot process with `NO_PROXY=10.0.15.4,127.0.0.1,localhost` so calculator requests bypass the proxy.
- Validation:
  - `curl --noproxy` against `/equip?equip_name=镇恶` returned HTTP 200 JSON.
  - `httpx` with `NO_PROXY` set returned HTTP 200 JSON while `HTTP_PROXY` remained configured.
  - Verified the restarted bot is connected to NapCat on `127.0.0.1:3001` with an established WebSocket connection.
- Follow-ups / Risks:
  - Future manual bot restarts need the same `NO_PROXY`/`no_proxy` runtime environment unless a persistent user/system environment variable is configured.

## 2026-05-19 - Local Calculator API URL

- Branch: rating
- Type: chore
- Files changed:
  - src/config/config.yml
  - worklog.md
- Summary:
  - Set local runtime `jx3.api.calculator_url` to `http://10.0.15.4:11223` for calculator-backed JX3 commands.
  - Normalized the URL without a trailing slash because code appends endpoint paths such as `/equip` and `/skill`.
  - Restarted the bot process to load the updated calculator URL.
- Validation:
  - Verified `src.config.Config.jx3.api.calculator_url` reads back as `http://10.0.15.4:11223`.
  - Verified TCP connectivity to `10.0.15.4:11223` succeeds.
  - Verified the restarted bot is connected to NapCat on `127.0.0.1:3001` with an established WebSocket connection.
- Follow-ups / Risks:
  - The calculator service root path timed out; test a real calculator-backed bot command to confirm endpoint behavior.

## 2026-05-19 - Local Bot Owner Permission

- Branch: rating
- Type: chore
- Files changed:
  - src/config/config.yml
  - worklog.md
- Summary:
  - Set local runtime `bot_basic.bot_owner` to QQ `245356865` so that account has owner-level permissions.
  - Restarted the bot process to load the updated owner configuration.
- Validation:
  - Verified the restarted bot is connected to NapCat on `127.0.0.1:3001` with an established WebSocket connection.
  - Confirmed `git status --short --branch` remains clean because the runtime config and worklog are locally excluded.
- Follow-ups / Risks:
  - Use `我的权限` in chat to confirm effective permissions from the bot side.

## 2026-05-19 - Local JX3API Runtime URL

- Branch: rating
- Type: chore
- Files changed:
  - src/config/config.yml
  - worklog.md
- Summary:
  - Set local ignored runtime config `jx3.api.url` to `https://api.jx3api.com` so JX3 commands such as `日常` build valid HTTP URLs.
  - Restarted the running bot process so the updated local config is loaded.
- Validation:
  - Called `get_daily_info()` locally after initializing NoneBot; it returned the expected daily JX3 activity text.
  - Verified the restarted bot is connected to NapCat on `127.0.0.1:3001` with an established WebSocket connection.
- Follow-ups / Risks:
  - Other JX3 commands may still need additional local config values such as API token, ticket, or specialized API URLs.

## 2026-05-19 - Repository Onboarding Documentation

- Branch: rating
- Type: docs
- Files changed:
  - AGENTS.md
  - worklog.md
- Summary:
  - Inspected the repository structure, dependency metadata, entry point, plugin layout, config template, database helpers, permission model, Docker files, and GitHub workflow.
  - Added repository-wide agent guidance for future contributions without changing existing bot code or tracked runtime behavior.
  - Added this worklog and documented the requirement to maintain it after every change.
- Validation:
  - Ran read-only repository inspection with `rg --files`, `git status --short --branch`, `git log --oneline -5`, and targeted `Get-Content` reads of key project files.
  - Ran `git diff --check`; no whitespace errors were reported.
  - Did not run application or test commands because this was a documentation-only change and the repository currently has no dedicated test suite configured.
- Follow-ups / Risks:
  - Future functional changes should run at least `pdm run python -m compileall bot.py config.py src` and `git diff --check`, then append a new worklog entry with the actual validation result.
