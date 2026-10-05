// Shared utilities across themes

#let render-text(txt) = {
  if type(txt) != str {
    return txt
  }
  let converted = txt.replace(regex("\*\*(.+?)\*\*"), m => "*" + m.captures.at(0) + "*")
  
  // Convert common LaTeX math commands to Typst math equivalents
  converted = converted.replace("\\Delta", "Delta")
                       .replace("\\alpha", "alpha")
                       .replace("\\beta", "beta")
                       .replace("\\gamma", "gamma")
                       .replace("\\lfloor", "floor(")
                       .replace("\\rfloor", ")")
                       .replace("\\leq", "<=")
                       .replace("\\geq", ">=")
                       .replace("\\times", "times")
                       .replace("\\in", "in")
  
  eval(converted, mode: "markup")
}

#let resolve-image-path(path) = {
  if path == none { return none }
  if path.starts-with("/") { path } else { "/" + path }
}
