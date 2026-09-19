#!/usr/bin/env python3
"""Embed an H.264/AAC MP4 as a RichMedia annotation in a PDF page.

The generated annotation follows Adobe's PDF 1.7 Extension Level 3
RichMedia dictionaries.  The video is stored inside the PDF; no local path or
companion file is required for playback.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)


def name(value: str) -> NameObject:
    return NameObject(value if value.startswith("/") else f"/{value}")


def embed_video(input_pdf: Path, output_pdf: Path, video: Path, page_number: int) -> None:
    reader = PdfReader(str(input_pdf))
    if page_number < 1 or page_number > len(reader.pages):
        raise ValueError(f"page {page_number} is outside 1..{len(reader.pages)}")

    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    page = writer.pages[page_number - 1]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    # RichMedia was introduced by Adobe as PDF 1.7 Extension Level 3.
    writer.pdf_header = "%PDF-1.7"
    root = writer.root_object
    extensions = root.get("/Extensions")
    if extensions is None:
        extensions = DictionaryObject()
        root[name("Extensions")] = extensions
    else:
        extensions = extensions.get_object()
    extensions[name("ADBE")] = DictionaryObject(
        {
            name("BaseVersion"): name("1.7"),
            name("ExtensionLevel"): NumberObject(3),
        }
    )

    media_stream = DecodedStreamObject()
    media_stream.set_data(video.read_bytes())
    media_stream[name("Type")] = name("EmbeddedFile")
    media_stream[name("Subtype")] = name("video#2Fmp4")
    media_stream[name("Params")] = DictionaryObject(
        {name("Size"): NumberObject(video.stat().st_size)}
    )
    media_ref = writer._add_object(media_stream)

    filename = video.name
    filespec = DictionaryObject(
        {
            name("Type"): name("Filespec"),
            name("F"): TextStringObject(filename),
            name("UF"): TextStringObject(filename),
            name("Desc"): TextStringObject("Build Abstract 1-minute demo"),
            name("EF"): DictionaryObject(
                {name("F"): media_ref, name("UF"): media_ref}
            ),
        }
    )
    filespec_ref = writer._add_object(filespec)

    instance = DictionaryObject(
        {
            name("Type"): name("RichMediaInstance"),
            name("Subtype"): name("Video"),
            name("Asset"): filespec_ref,
        }
    )
    instance_ref = writer._add_object(instance)

    configuration = DictionaryObject(
        {
            name("Type"): name("RichMediaConfiguration"),
            name("Subtype"): name("Video"),
            name("Name"): TextStringObject("Build Abstract demo"),
            name("Instances"): ArrayObject([instance_ref]),
        }
    )
    configuration_ref = writer._add_object(configuration)

    activation = DictionaryObject(
        {
            name("Type"): name("RichMediaActivation"),
            # Start when the slide becomes visible; no external-file dialog or
            # invisible link target is involved.
            name("Condition"): name("PV"),
            name("Configuration"): configuration_ref,
            name("Presentation"): DictionaryObject(
                {
                    name("Style"): name("Embedded"),
                    name("Toolbar"): BooleanObject(True),
                    name("NavigationPane"): BooleanObject(False),
                    name("PassContextClick"): BooleanObject(True),
                }
            ),
        }
    )
    deactivation = DictionaryObject(
        {
            name("Type"): name("RichMediaDeactivation"),
            name("Condition"): name("PI"),
        }
    )

    content = DictionaryObject(
        {
            name("Type"): name("RichMediaContent"),
            name("Assets"): DictionaryObject(
                {
                    name("Names"): ArrayObject(
                        [TextStringObject(filename), filespec_ref]
                    )
                }
            ),
            name("Configurations"): ArrayObject([configuration_ref]),
        }
    )

    # A transparent appearance keeps the Beamer poster visible until playback.
    appearance = DecodedStreamObject()
    appearance.set_data(b"q\nQ\n")
    appearance[name("Type")] = name("XObject")
    appearance[name("Subtype")] = name("Form")
    appearance[name("FormType")] = NumberObject(1)
    appearance[name("BBox")] = ArrayObject(
        [FloatObject(0), FloatObject(0), FloatObject(width), FloatObject(height)]
    )
    appearance[name("Resources")] = DictionaryObject()
    appearance_ref = writer._add_object(appearance)

    annotation = DictionaryObject(
        {
            name("Type"): name("Annot"),
            name("Subtype"): name("RichMedia"),
            name("Rect"): ArrayObject(
                [FloatObject(0), FloatObject(0), FloatObject(width), FloatObject(height)]
            ),
            name("NM"): TextStringObject("buildabstract-demo"),
            name("Contents"): TextStringObject("Build Abstract 1-minute demo"),
            name("F"): NumberObject(4),
            name("Border"): ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)]),
            name("AP"): DictionaryObject({name("N"): appearance_ref}),
            name("RichMediaContent"): content,
            name("RichMediaSettings"): DictionaryObject(
                {
                    name("Activation"): activation,
                    name("Deactivation"): deactivation,
                }
            ),
        }
    )
    annotation_ref = writer._add_object(annotation)
    annotation[name("P")] = page.indirect_reference

    annots = page.get("/Annots")
    if annots is None:
        page[name("Annots")] = ArrayObject([annotation_ref])
    else:
        annots = annots.get_object()
        # Ensure an old run:/Launch overlay cannot survive on the video page.
        kept = ArrayObject()
        for ref in annots:
            obj = ref.get_object()
            action = obj.get("/A")
            if action and action.get_object().get("/S") == name("Launch"):
                continue
            kept.append(ref)
        kept.append(annotation_ref)
        page[name("Annots")] = kept

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as handle:
        writer.write(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("video", type=Path)
    parser.add_argument("--page", type=int, default=11)
    args = parser.parse_args()
    embed_video(args.input_pdf, args.output_pdf, args.video, args.page)


if __name__ == "__main__":
    main()
