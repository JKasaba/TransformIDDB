def generate_urn(organization, colorspace_in, colorspace_out, aces_version, transform_version):
    # Strip leading/trailing whitespace and replace spaces with underscores
    organization = organization.strip().replace(" ", "_")
    colorspace_in = colorspace_in.strip().replace(" ", "_")
    colorspace_out = colorspace_out.strip().replace(" ", "_")
    aces_version = aces_version.strip().replace(" ", "_")
    transform_version = transform_version.strip().replace(" ", "_")
    
    urn_template = "<ACEStransformID>urn:ampas:aces:transformId:v1.5:ACEScsc.<organization>.<Colorspace_In>_to_<Colorspace_out>.<aces_version>.<transform_version></ACEStransformID>"
    urn = urn_template.replace("<organization>", organization) \
                      .replace("<Colorspace_In>", colorspace_in) \
                      .replace("<Colorspace_out>", colorspace_out) \
                      .replace("<aces_version>", aces_version) \
                      .replace("<transform_version>", transform_version)
    return urn

# Example usage:
# organization = "Canon"
# colorspace_in = "Rec709"
# colorspace_out = "ACES cg"
# aces_version = "v1.2"
# transform_version = "v3.0"

# urn = generate_urn(organization, colorspace_in, colorspace_out, aces_version, transform_version)
# print(urn)

