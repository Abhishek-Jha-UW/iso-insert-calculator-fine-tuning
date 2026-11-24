# ISO Insert Calculator

A Streamlit app that decodes turning insert part numbers and estimates volume and weight per insert.

## Input and results

Upload a UTF-8 CSV or the first worksheet of an XLSX file with a `part_number` or `Name` column. Add an optional `hole_diameter_mm` column if you know a row's through-hole diameter. The sample includes an illustrative hole diameter. Use the actual drawing value for your parts. Select **Auto**, **ISO metric**, or **ANSI inch**, and optionally supply a batch density in g/cm³. Separate the three ANSI dimension tokens with spaces if the compact designation is ambiguous.

The decoder accepts compact or spaced designations and retains trailing labels such as `Z1`, `W`, and `R-Wiper` separately from the normalized designation. It recognizes the round insert `M0` marker whether attached, spaced, or hyphenated. Geometry stays blank when a size or thickness code is absent from the rule tables.

Download the Excel template from the sidebar and paste designations into the first worksheet. The app preserves input order, flags individual rows that need review, and exports detailed fields and assumptions as an Excel workbook. Weight is reported in grams using estimated volume in mm³ multiplied by density in g/cm³ and divided by 1,000.

Select a material grade to use its batch density from `rules/grade_densities.csv`, transcribed from the supplied Toolmaker Solutions grade chart. Use **Custom density** for an unlisted material. A grade with no published density in the chart accepts a manual value or leaves weight blank. The results workbook records the grade and density used.

Open **Tolerance reference** for limits by class, including the shape and size lookup for class M. Use **Show per-insert tolerances** to compare the resolved limits in the results table. **Exceptions** lists rows with incomplete geometry or input errors.

## Geometry assumptions

The fine-tuning version applies the catalog dimensions in `rules/catalog_dimension_overrides.json` to matching normalized ISO base designations. The results workbook identifies the dimension basis and catalog URL. Suffix variants use these base dimensions for estimates. Catalog values for another manufacturer's part do not establish the dimensions of a particular suffix variant. Trigon inserts still report dimensions only because the calculator has no trigon volume model.

Gross volume uses an ideal circular, rhombic, or regular polygon body. It uses the nominal inscribed circle at the cutting face and tapers the profile by the coded clearance angle over the nominal thickness. The model excludes corner rounding, countersinks, chipbreakers, coatings, and other manufacturer-specific detail. A supplied through-hole diameter deducts a centered cylinder. When its diameter is unknown, a coded fixing hole is excluded from deductions and the estimate equals gross volume. The results are approximate and can differ from measured part weights.

Some codes decode to dimensions but lack sufficient information for the geometry model. This includes the trigon outline, shapes missing a size lookup, and special clearance angles. See the row notes for coverage. Keep the JSON tables synchronized with the Markdown when revising the rules.

## Run locally

Use Python 3.12.

```shell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push the contents of this folder to the root of a GitHub repository.
2. Create a Streamlit Community Cloud app using that repository and select `app.py` as the entry point.
3. In **Advanced settings → Secrets**, add the API key and, optionally, the model override.

```toml
OPENAI_API_KEY = "your-key-here"
# OPENAI_MODEL = "gpt-6-luna"
```

Use the same values in a local `.streamlit/secrets.toml` file for local AI assistance. The local secrets file is ignored by Git. The deployed app reads the key in the background, and users never enter a key.

AI guidance runs only when requested. It can suggest an indicative material density range or explain a selected result. It sends the material text and selected calculation fields to OpenAI and leaves calculation inputs untouched. Uploaded files are processed by the app, and the calculator works without AI configuration.
