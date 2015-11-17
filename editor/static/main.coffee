reload = ->
  loadJson "/sourcefiles", (sourceFiles) ->
    loadJson "/log/data.json", (logData) ->
      render(sourceFiles, logData)

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
