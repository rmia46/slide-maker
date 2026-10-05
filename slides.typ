#import "template/theme.typ": *

#let data = yaml("slides.yaml")

#show: presentation.with(
  meta: data.at("meta", default: (:))
)

#render-deck(data)
