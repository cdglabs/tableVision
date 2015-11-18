
# =============================================================================
# Model
# =============================================================================

model = new class
  constructor: ->
    @sourceFiles = [] # {name, content}
    @logData = [] # {line, image, file}
    @selectedFileName = false

  selectedFile: ->
    return @sourceFiles.find (sourceFile) =>
      sourceFile.name == @selectedFileName

  selectFile: (fileName) ->
    @selectedFileName = fileName

reload = ->
  loadJson "/sourcefiles", (sourceFiles) ->
    loadJson "/log/data.json", (logData) ->
      model.sourceFiles = sourceFiles
      model.logData = logData
      if !model.selectedFileName
        model.selectedFileName = sourceFiles[0].name
      render()

render = ->
  contentEl = document.querySelector("#content")
  R.render(R.App(), contentEl)


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

R.create "App",
  render: ->
    R.div {},
      R.Files {}
      R.SourceCode {}

R.create "Files",
  render: ->
    R.div {className: "Files"},
      for sourceFile in model.sourceFiles
        R.File {sourceFile, key: sourceFile.name}

R.create "File",
  render: ->
    {name, content} = @props.sourceFile
    isSelected = (name == model.selectedFileName)
    R.div {
      className: R.cx {
        "File": true
        "Selected": isSelected
      }
      onClick: @onClick
    },
      R.div {className: "FileName"}, name
      R.div {className: "FileImages"},
        for entry in model.logData
          if entry.file == name
            R.img {src: "/log/" + entry.image, key: entry.image}

  onClick: ->
    {name, content} = @props.sourceFile
    model.selectFile(name)
    render()



R.create "SourceCode",
  render: ->
    R.div {className: "SourceCode"}

  componentDidMount: ->
    el = R.findDOMNode(this)

    @mirror = CodeMirror(el, {
      mode: "python"
      theme: "material"

      smartIndent: true
      indentUnit: 4

      matchBrackets: true
      autoCloseBrackets: true
      styleActiveLine: true

      # lineNumbers: true
      extraKeys: {
        # Indent with spaces, not tabs.
        Tab: (cm) ->
          spaces = Array(cm.getOption("indentUnit") + 1).join(" ")
          cm.replaceSelection(spaces)
      }
    })

    @componentDidUpdate()

  componentDidUpdate: ->
    sourceFile = model.selectedFile()

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


# =============================================================================
# Utility
# =============================================================================

loadJson = (url, callback) ->
  xhr = new XMLHttpRequest()
  xhr.onreadystatechange = =>
    return unless xhr.readyState == 4
    return unless xhr.status == 200
    jsonString = xhr.responseText
    callback(JSON.parse(jsonString))
  xhr.open("GET", url, true)
  xhr.send()


# =============================================================================
# Bootstrap
# =============================================================================

reload()
