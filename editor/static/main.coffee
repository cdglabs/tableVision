



# =============================================================================
# R: Convenience API into React
# =============================================================================

R = window.R = {}

# Provide easy access to React.DOM
for own key, value of React.DOM
  R[key] = value

# Utility (from React.addons.classSet)
R.cx = (classNames) ->
  Object.keys(classNames).filter((className) -> classNames[className]).join(" ")

R.create = (name, spec) ->
  # Component.displayName is used by React in its debugging messages.
  spec.displayName = name
  component = React.createClass(spec)
  R[name] = React.createFactory(component)

R.render = ReactDOM.render
R.findDOMNode = ReactDOM.findDOMNode


# =============================================================================
# Views
# =============================================================================

R.create "SourceCode",
  render: ->
    R.div {}

  componentDidMount: ->
    el = R.findDOMNode(this)

    @mirror = CodeMirror(el, {
      mode: "python"
      theme: "material"

      smartIndent: true
      indentUnit: 4

      lineNumbers: true
    })

    @componentDidUpdate()

  componentDidUpdate: ->
    {sourceFile} = @props

    @mirror.setValue(sourceFile.content)

    for entry in model.logData
      if entry.file == sourceFile.name
        imgEl = document.createElement("img")
        imgEl.src = "/log/" + entry.image
        lineText = @mirror.getLine(entry.line)
        indent = lineText.replace(/[^ ].*/, "").length
        imgEl.style.marginLeft = indent * 9 + "px"
        @mirror.addLineWidget(entry.line-1, imgEl)


    # @mirror.on("change", @_onChange)
    # @mirror.on("mousedown", @_onMirrorMouseDown)
    # @componentDidUpdate()

  # componentDidUpdate: ->
  #   @_updateMirrorFromAttribute()

  # _onChange: ->
  #   @_updateAttributeFromMirror()
  #   if @mirror.hasFocus()
  #     @_showAutocomplete()

  # _onMirrorMouseDown: (mirror, mouseDownEvent) ->
  #   el = mouseDownEvent.target
  #   if Util.matches(el, ".cm-number")
  #     mouseDownEvent.preventDefault()
  #     @_startNumberScrub(mouseDownEvent)

  # _onMouseUp: (mouseUpEvent) ->
  #   {attribute} = @props
  #   {dragManager} = @context
  #   if dragManager.drag?.type == "transcludeAttribute"
  #     @transcludeAttribute(dragManager.drag.attribute)




model = {
  sourceFiles: []
  logData: []
}

reload = ->
  loadJson "/sourcefiles", (sourceFiles) ->
    loadJson "/log/data.json", (logData) ->
      model.sourceFiles = sourceFiles
      model.logData = logData

      contentEl = document.querySelector("#content")
      R.render(R.SourceCode({sourceFile: sourceFiles[0]}), contentEl)


render = (sourceFiles, logData) ->
  contentEl = document.querySelector("#content")
  contentEl.innerHTML = ""

  mirror = CodeMirror(contentEl, {
    mode: "python"
    theme: "material"
    value: "\n"
  })

  titles = []
  logEntries = []
  allCode = ""

  for sourceFile in sourceFiles
    startLine = allCode.split("\n").length - 1

    titles.push({
      name: sourceFile.name
      line: startLine
    })

    for datum in logData
      if datum.file == sourceFile.name
        logEntries.push({
          line: startLine + datum.line,
          image: datum.image
        })

    allCode += "\n" + sourceFile.content

  mirror.setValue(allCode)

  for title in titles
    titleEl = document.createElement("h1")
    titleEl.innerText = title.name
    mirror.addLineWidget(title.line, titleEl)

  for entry in logEntries
    imgEl = document.createElement("img")
    imgEl.src = "/log/" + entry.image
    lineText = mirror.getLine(entry.line)
    indent = lineText.replace(/[^ ].*/, "").length
    imgEl.style.marginLeft = indent * 9 + "px"
    mirror.addLineWidget(entry.line, imgEl)


loadJson = (url, callback) ->
  xhr = new XMLHttpRequest()
  xhr.onreadystatechange = =>
    return unless xhr.readyState == 4
    return unless xhr.status == 200
    jsonString = xhr.responseText
    callback(JSON.parse(jsonString))
  xhr.open("GET", url, true)
  xhr.send()


reload()
