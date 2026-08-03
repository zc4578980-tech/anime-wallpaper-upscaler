# Anime Screenshot Promotion Design

## Status

Approved direction. This document defines the user-facing positioning and evidence structure;
it does not authorize publication, external posting, or a GitHub Release.

## Goal

Reposition Anime Wallpaper Upscaler for ordinary Windows anime viewers around a concrete job:
turning a personally captured anime frame into a screen-ready wallpaper. The promotion must make
that outcome understandable before explaining Real-ESRGAN, the Agent Skill, or implementation
details.

The first-month target remains 30 net new GitHub Stars from the recorded release-day baseline.
This is a measured outcome target, not a forecast or guarantee.

## Primary Audience

The first audience is an ordinary Windows user who:

- pauses an anime episode on a frame they like;
- wants that frame as a desktop wallpaper;
- does not want to install models or learn command-line options;
- cares about visible detail, complete composition, and correct screen fit.

Codex and other Agent users are a secondary audience. Agent invocation remains a differentiator,
but it must not compete with the screenshot-to-wallpaper promise in the first viewport.

## Message Architecture

The approved Chinese message pair is:

> **暂停喜欢的一帧，把它留在桌面。**
>
> 番剧截图一键超分，自动生成适配当前屏幕、保留完整构图的高清 Windows 壁纸。

The approved English message pair is:

> **Pause a frame. Keep it on your desktop.**
>
> Turn anime screenshots into screen-ready Windows wallpapers while preserving the complete
> composition.

The main promise is followed by four concise proof points:

- drag-and-drop workflow after setup;
- local processing without uploading the screenshot;
- automatic physical-screen and Vulkan GPU detection;
- 2x, 3x, and 4x output through the official Real-ESRGAN NCNN/Vulkan runtime.

"One click" describes the post-setup user experience, not the first installation. Installation
still requires reviewing upstream terms and approving the verified runtime download. Copy must
not claim that upscaling recreates every detail missing from the source or that every output is
native 4K.

## README Information Order

The English and Chinese README files use the same information hierarchy:

1. Product name, emotional headline, functional subhead, and Windows/local-processing proof.
2. A real anime screenshot transformation showing the original frame, a truthful detail
   comparison, and the finished desktop wallpaper.
3. A three-step ordinary-user path: download the latest Windows ZIP, run `install.cmd`, then drag
   a screenshot onto the desktop shortcut.
4. A compact explanation of full-composition preservation and automatic screen adaptation.
5. Technical attribution to official Real-ESRGAN, ncnn, and Vulkan.
6. Agent Skill usage as an advanced workflow.
7. Detailed installation, CLI, recovery, licensing, and troubleshooting material.

The existing technical comparison table remains useful below the first-use workflow. It no
longer carries the burden of explaining the product before the user sees the outcome.

## Visual Evidence

The approved campaign uses a real anime screenshot supplied by the user in the repository README,
GitHub Release material, social preview, and external promotional images. This choice has a known
copyright risk and is not represented as rights-safe.

The evidence sequence is:

1. **Source frame:** the complete screenshot at its original dimensions.
2. **Detail comparison:** the same local crop on both sides at the same displayed pixel size. The
   left side is labeled `Original screenshot`; the right side is labeled `Real-ESRGAN 4x` or the
   actual scale used. No side may receive extra sharpening that the other side does not receive.
3. **Wallpaper result:** the final composition-preserving output displayed on the user's real
   Windows desktop. The image must show the complete screen rather than a decorative device mockup.
4. **Compact social version:** a readable crop of the same verified source and output, with the
   screenshot-to-wallpaper message and repository name.

All presentation assets derive from one recorded inference run. The source path, exact command,
model, scale, target resolution, GPU selection, output paths, and image dimensions are recorded in
an adjacent evidence note so the transformation is reproducible.

The comparison must demonstrate actual resolution and wallpaper-composition differences. It must
not present a deliberately blurred or degraded source as the original, invent missing source
detail, or imply that the wrapper owns the Real-ESRGAN model.

## Copyright Disclosure And Takedown Handling

The user explicitly chose to use a real anime screenshot despite not establishing a redistribution
license. A statement such as "copyright belongs to the rightsholder; contact for removal" does not
grant a license, prevent a DMCA request, or eliminate liability. Repository and campaign copy must
not describe the asset as licensed, fair use, or rights-safe without supporting evidence.

Before the promotional change can merge, the asset notice must record:

- anime title, episode, and timestamp when known;
- screenshot source and the identified rightsholder or production committee when known;
- that the frame is used to demonstrate processing of a user-supplied screenshot;
- that the project is unaffiliated with and not endorsed by the rightsholder;
- a GitHub Issue contact path for a removal request;
- the exact repository files to replace if removal is requested.

The notice should use professional factual language rather than relying only on the Chinese phrase
"侵删". If a removal request arrives, the image and derived assets are removed in a dedicated
commit and replaced with the existing deterministic original fixture. Git history may still retain
the prior blobs; a valid GitHub or legal removal request is handled through the applicable platform
process rather than by claiming that a normal commit erases history.

## Release And Branch Boundaries

The promotion must not point ordinary users to the known-conflicting v0.2.1 installer as the final
recommended path. Sequence the work as follows:

1. review and publish the separately authorized v0.2.2 installer hotfix through protected `main`;
2. verify the downloadable v0.2.2 ZIP on a Windows machine with an existing Skill junction;
3. update README and promotional assets in a separate pull request;
4. publish or edit public channel posts only after separate channel authorization.

The promotion branch may be based on the v0.2.2 candidate but must not bypass its CI, PR, merge,
tag, or Release approval gates.

## Measurement

GitHub traffic is evaluated as a funnel rather than treating clone counts as users:

```text
qualified unique visitor -> README proof viewed -> Release clicked
                         -> ZIP downloaded -> successful use -> Star
```

Record Stars, unique visitors, views, top referrer, and Windows ZIP downloads at the existing day
1, 3, 7, 14, and 30 checkpoints. Record each external placement with its URL and timestamp. Do not
count the owner's repeated downloads, Actions activity, artificial Stars, paid Stars, or
unsupported clone interpretations as organic adoption.

## Acceptance Criteria

- The first viewport explains the screenshot-to-wallpaper outcome before technical architecture.
- The English and Chinese README versions carry equivalent promises and installation steps.
- The real screenshot, detail crop, and desktop result come from one reproducible inference run.
- Labels state the actual scale, target resolution, and composition mode.
- The public asset notice contains the source, affiliation disclaimer, contact route, and removal
  map described above.
- The latest recommended download completes setup when another Codex Skill path already exists.
- Every statement about local processing, upstream ownership, model behavior, and screen fitting
  matches the tested implementation.
- All Markdown links and images render on the GitHub repository page without broken paths or
  unreadable text at desktop and mobile widths.
- The change introduces no new inference model, GUI, telemetry, upload service, or tracking code.

## Non-Goals

- claiming an original super-resolution algorithm or model;
- promising perfect reconstruction of details absent from the screenshot;
- adding a complex GUI solely for promotion;
- guaranteeing 30 Stars or substituting artificial engagement for organic interest;
- distributing full episodes, source video, or a wallpaper pack extracted from copyrighted anime.

## Approved Decisions

- Primary audience: ordinary Windows anime viewers.
- Primary job: anime screenshot to screen-ready wallpaper.
- Message style: emotional hook followed by a precise functional promise.
- Agent Skill: secondary proof and advanced workflow.
- Visual material: real anime screenshot in README, Release, social preview, and external posts.
- Copyright posture: disclose the unlicensed status and removal path; do not claim that disclosure
  creates permission.
